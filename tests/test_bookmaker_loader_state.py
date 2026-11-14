"""Synthetic loader contracts, NOT a native StatsHub HTML or feed capture.

WIRE was independently generated with turbo-stream@2.4.1 (npm encode), rather
than by the decoder under test. All fixture values and credentials are fake.
"""
from __future__ import annotations

import copy
import json
import socket

import pytest

from edgefactory.sources.bookmaker_context_snapshot import (
    inspect_native_data_loading,
    inspect_native_loader_state,
)

URL='https://statshub.sportradar.com/sportpesa/en/match/75879092'
WIRE='''[{"_1":2,"_16":-5,"_17":-5},"loaderData",{"_3":4},"root",{"_5":6},"cctx",{"_7":8,"_9":10,"_11":8,"_12":13,"_14":15},"clientId","sportpesa","fishnetUrl","https://widgets.fn.sportradar.com/","fishnetClientAlias","language","en","fishnetToken","DO_NOT_PRINT","errors","actionData"]\n'''
STATE={'loaderData':{'root':{'cctx':{
    'clientId':'sportpesa','fishnetUrl':'https://widgets.fn.sportradar.com/',
    'fishnetClientAlias':'sportpesa','language':'en','fishnetToken':'DO_NOT_PRINT'}}},
    'errors':None,'actionData':None}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args,**kwargs): raise AssertionError('loader decoding must not use network')
    monkeypatch.setattr(socket,'socket',deny)
    monkeypatch.setattr(socket,'create_connection',deny)


def enqueue(value):
    return 'window.__reactRouterContext.streamController.enqueue('+json.dumps(value)+');'


def html(script,attrs=''):
    close = '<script>window.__reactRouterContext.streamController.close();</script>' if 'streamController.enqueue' in script else ''
    return ('<html><head><script '+attrs+'>'+script+'</script>'+close+'</head></html>').encode()


def direct(state=None):
    return html(json.dumps(STATE if state is None else state),'type="application/json"')


def assert_held(result):
    assert result['decoded_context_row_count']==result['admitted_rows']==result['api_requests_made']==0
    assert not result['javascript_executed']
    assert result['kickoff_utc'] is None and result['fixture_binding_status']=='not_verified'
    assert result['field_validation_status']=='native_loader_fixture_not_available'
    assert 'DO_NOT_PRINT' not in json.dumps(result)


@pytest.mark.parametrize('body,fmt',[
    (html(enqueue(WIRE)),'react_router_turbo_stream_v2_json_subset'),
    (direct(),'application_json_loader_data'),
])
def test_supported_loader_state_capture_and_safe_config_validation(body,fmt):
    r=inspect_native_loader_state(body,URL)
    assert r['status']=='decoded_supported_loader_state'
    assert r['serialization_format']==fmt and r['decoded_loader_state_count']==1
    assert r['loader_route_count']==1 and r['root_context_present']
    assert r['feed_config']=={'feed_origin':'https://widgets.fn.sportradar.com',
        'client_brand_bound':True,'language_bound':True,'client_alias_has_supported_syntax':True,
        'token_present_nonempty_text':True,'syntactically_complete':True}
    assert not r['page_loader_errors_present']
    assert_held(r)


def test_split_enqueue_literal_decoding_without_evaluation():
    bodies=''.join('<script>'+enqueue(p)+'</script>' for p in (WIRE[:41],WIRE[41:97],WIRE[97:]))
    bodies+='<script>window.__reactRouterContext.streamController.close();</script>'
    r=inspect_native_loader_state(bodies.encode(),URL+'/statistics')
    assert r['decoded_loader_state_count']==1 and r['transfer_chunk_count']==3
    assert_held(r)


def test_repeated_literal_calls_in_one_script():
    r=inspect_native_loader_state(html(enqueue(WIRE[:70])+'\n'+enqueue(WIRE[70:])),URL)
    assert r['decoded_loader_state_count']==1 and r['transfer_chunk_count']==2


@pytest.mark.parametrize('wrapper',[
    lambda s:'<template>'+s+'</template>',lambda s:'<noscript>'+s+'</noscript>',
    lambda s:'<!--'+s+'-->',
    lambda s:s.replace('<script>','<script src="/assets/feeds-x.js">'),
    lambda s:s.replace('<script>','<script type="application/ld+json">'),
    lambda s:s.replace('<script>','<script type="text/plain">'),
])
def test_inert_external_or_nonexecutable_script_is_not_a_loader(wrapper):
    r=inspect_native_loader_state(wrapper('<script>'+enqueue(WIRE)+'</script>').encode(),URL)
    assert r['status']=='no_supported_transfer_found' and not r['decoded_loader_state_count']


@pytest.mark.parametrize('script',[
    'eval('+json.dumps(enqueue(WIRE))+');',
    enqueue(WIRE)+'alert("DO_NOT_PRINT")',
    enqueue(WIRE).replace(');',' + window.secret);'),
    'window.__reactRouterContext.streamController.enqueue(JSON.parse("[]"));',
    'window.__reactRouterContext.streamController.enqueue("\\x5b\\x5d");',
    'window.__reactRouterContext.streamController.enqueue({"loaderData":{}});',
    enqueue(WIRE).replace(');',')'),
])
def test_javascript_wrappers_expressions_and_non_json_arguments_never_run(script):
    r=inspect_native_loader_state(html(script),URL)
    assert r['decoded_loader_state_count']==0
    assert_held(r)


@pytest.mark.parametrize('wire',[
    '[{"_1":true},"loaderData"]', '[{"_1":999},"loaderData"]',
    '[{"_1":-1},"loaderData"]', '[{"_1":-2},"loaderData"]',
    '[{"_1":-6},"loaderData"]', '[{"_1":0},"loaderData"]',
    '[{"not_a_reference":1},"loaderData"]', '[{"_1":2},5,{}]',
    '[{"_1":2,"_3":2},"loaderData",{},"loaderData"]',
    '[{"_1":2,"_1":3},"loaderData",{},{}]',
    '[{"_1":2},"loaderData",["P",3],"DO_NOT_PRINT"]',
    '[{"_1":2},"loaderData",["SingleFetchClassInstance",3],{}]',
    '[{"_1":2},"loaderData",["D","2026-11-01"]]',
    WIRE+'P10:[]\n', WIRE+WIRE,
    '[NaN]', '[1e400]', '[]', '{}',
])
def test_unsupported_reference_graph_or_deferred_frames_fail_closed(wire):
    r=inspect_native_loader_state(html(enqueue(wire)),URL)
    assert not r['decoded_loader_state_count']
    assert_held(r)


def test_undefined_reference_is_not_false_or_null_data():
    wire=WIRE.replace('"_16":-5','"_16":-7')
    r=inspect_native_loader_state(html(enqueue(wire)),URL)
    assert r['decoded_loader_state_count']==1 and not r['page_loader_errors_present']


@pytest.mark.parametrize('state',[{}, {'loaderData':[]}, {'loaderData':None}])
def test_non_loader_documents_not_promoted_to_stats(state):
    r=inspect_native_loader_state(direct(state),URL)
    assert r['decoded_loader_state_count']==0
    assert_held(r)


def test_ambiguous_direct_and_stream_states_rejected():
    for body in (direct()+direct(),direct()+html(enqueue(WIRE))):
        r=inspect_native_loader_state(body,URL)
        assert r['status']=='ambiguous_loader_state' and not r['decoded_loader_state_count']


def test_close_then_enqueue_is_not_a_complete_stream():
    body=html('window.__reactRouterContext.streamController.close();')+html(enqueue(WIRE))
    assert inspect_native_loader_state(body,URL)['status']=='unsupported_transfer_script'


@pytest.mark.parametrize('key,value',[
    ('clientId','other-client'),('language','fr'),('fishnetClientAlias','DO NOT PRINT'),
    ('fishnetToken',''),('fishnetToken',False),('fishnetToken',' '),
    ('fishnetUrl','https://user:DO_NOT_PRINT@widgets.fn.sportradar.com/'),
    ('fishnetUrl','https://widgets.fn.sportradar.com/?T=DO_NOT_PRINT'),
    ('fishnetUrl','https://evil.example/'),('fishnetUrl','https://127.0.0.1/'),
    ('fishnetUrl','http://widgets.fn.sportradar.com/'),
    ('fishnetUrl','https://widgets.fn.sportradar.com:443/'),
    ('fishnetUrl','https://widgets.fn.sportradar.com.evil.example/'),
    ('fishnetUrl','https://[invalid'),
    ('fishnetUrl',' https://widgets.fn.sportradar.com/'),
])
def test_bad_config_never_becomes_complete_or_leaks_values(key,value):
    state=copy.deepcopy(STATE)
    state['loaderData']['root']['cctx'][key]=value
    r=inspect_native_loader_state(direct(state),URL)
    assert r['decoded_loader_state_count']==1
    assert not r['feed_config']['syntactically_complete']
    assert 'evil.example' not in json.dumps(r) and 'DO NOT PRINT' not in json.dumps(r)
    assert_held(r)


def test_structural_payload_counts_are_not_decoded_stats_or_regulation_results():
    state=copy.deepcopy(STATE)
    state['loaderData']['root']['cache']={'DO_NOT_PRINT':{'doc':[{'data':{
        'match':{'teams':{'home':'DO_NOT_PRINT'},'results':{'AP':[4,3]}},
        'tables':[],'standings':[]}}]}}
    state['errors']={'root':'DO_NOT_PRINT'}
    r=inspect_native_loader_state(direct(state),URL)
    assert r['payload_structure_counts']=={'doc0_data_envelopes':1,'match':1,'teams':1,
                                          'results':1,'standings':1,'tables':1,'queries':0}
    assert r['page_loader_errors_present']
    assert_held(r)


@pytest.mark.parametrize('body',[
    b'\xff',b'<script>unfinished',
    direct({'loaderData':{'root':{'x':'a'*(512*1024)}}}),
    html(enqueue(' '*((512*1024)+1))),
    html(enqueue('['*1000+']'*1000)),
    html(enqueue(json.dumps([{'_1':2},'loaderData']+[0]*20001))),
    html(enqueue(json.dumps(['x']*40001))),
])
def test_limits_and_malformed_serialization_fail_closed(body):
    r=inspect_native_loader_state(body,URL)
    assert not r['decoded_loader_state_count']
    assert_held(r)


def test_native_byte_and_url_guards_before_parsing():
    for body,url in ((b'x'*(2*1024*1024+1),URL),(b'',URL+'?T=DO_NOT_PRINT')):
        with pytest.raises(ValueError):inspect_native_loader_state(body,url)


def test_existing_discovery_reuses_same_loader_decoder_without_network():
    r=inspect_native_data_loading(html(enqueue(WIRE)),URL)
    assert r['loader_state']['decoded_loader_state_count']==1
    assert r['api_requests_made']==0
    assert 'DO_NOT_PRINT' not in json.dumps(r)



def test_complete_initial_json_without_stream_close_is_not_complete_capture():
    body=('<script>'+enqueue(WIRE)+'</script>').encode()
    r=inspect_native_loader_state(body,URL)
    assert r['status']=='incomplete_loader_stream' and not r['decoded_loader_state_count']


def test_shared_graph_is_memoized_not_expanded_exponentially():
    values=json.loads(WIRE)
    values[4]['_18']=19
    values.append('cache')
    for i in range(19,54):
        values.append([i+1,i+1])
    values.append([])
    r=inspect_native_loader_state(html(enqueue(json.dumps(values))),URL)
    assert r['decoded_loader_state_count']==1
    assert_held(r)


def test_excessive_reference_graph_depth_is_rejected():
    values=json.loads(WIRE)
    values[4]['_18']=19
    values.append('cache')
    for i in range(19,119):values.append([i+1])
    values.append([])
    r=inspect_native_loader_state(html(enqueue(json.dumps(values))),URL)
    assert r['status']=='loader_structure_limit' and not r['decoded_loader_state_count']


# Independently generated with npm turbo-stream@2.4.1 encode. Synthetic, not a
# native StatsHub capture: undefined, null, nonfinite values, -0 and a sparse slot.
WIRE_SPECIAL='''[{"_1":2,"_19":-5},"loaderData",{"_3":4},"root",{"_5":6,"_16":17},"cctx",{"_7":8,"_9":10,"_11":12,"_13":8,"_14":15},"clientId","sportpesa","language","en","fishnetUrl","https://widgets.fn.sportradar.com/","fishnetClientAlias","fishnetToken","DO_NOT_PRINT","cache",[-7,-5,-2,-6,-3,-4,-1,18],42,"errors"]\n'''


def test_stock_v2_special_values_decode_without_numeric_or_null_substitution():
    from edgefactory.sources.bookmaker_context_snapshot import (
        _LOADER_HOLE,
        _LOADER_NAN,
        _LOADER_NEGATIVE_INFINITY,
        _LOADER_POSITIVE_INFINITY,
        _LOADER_UNDEFINED,
        _unpack_loader_v2,
    )
    state=_unpack_loader_v2(json.loads(WIRE_SPECIAL))
    cache=state['loaderData']['root']['cache']
    assert len(cache)==8
    assert cache[0] is _LOADER_UNDEFINED
    assert cache[1] is None
    assert cache[2] is _LOADER_NAN
    assert cache[3] is _LOADER_POSITIVE_INFINITY
    assert cache[4] is _LOADER_NEGATIVE_INFINITY
    assert str(cache[5])=='-0.0'
    assert cache[6] is _LOADER_HOLE
    assert cache[7]==42
    assert len({id(cache[i]) for i in (0,1,2,3,4,6)})==6
    r=inspect_native_loader_state(html(enqueue(WIRE_SPECIAL)),URL)
    assert r['decoded_loader_state_count']==1
    assert r['feed_config']['syntactically_complete']
    assert r['wire_special_value_counts']=={
        'undefined':1,'array_hole':1,'nan':1,'negative_infinity':1,
        'positive_infinity':1,'negative_zero':1}
    assert_held(r)


@pytest.mark.parametrize('ref,reason',[
    (-1,'array_hole_outside_array'),(-8,'unknown_negative_reference'),
    (1000000,'reference_out_of_range'),(True,'noninteger_reference'),
    (1.0,'noninteger_reference'),('DO_NOT_PRINT','noninteger_reference'),
])
def test_bad_references_still_rejected_with_value_free_reason(ref,reason):
    values=json.loads(WIRE)
    values[0]['_1']=ref
    r=inspect_native_loader_state(html(enqueue(json.dumps(values))),URL)
    assert r['status']=='invalid_reference' and r['reference_failure_kind']==reason
    assert not r['decoded_loader_state_count']
    assert_held(r)


@pytest.mark.parametrize('ref',[-2,-3,-6,-7])
def test_special_value_cannot_validate_credential_or_origin(ref):
    values=json.loads(WIRE)
    values[6]['_9']=ref  # fishnetUrl becomes unavailable, NOT a default host.
    r=inspect_native_loader_state(html(enqueue(json.dumps(values))),URL)
    assert r['decoded_loader_state_count']==1
    assert not r['feed_config']['syntactically_complete']
    assert r['feed_config']['feed_origin'] is None
    assert_held(r)


def test_only_sparse_array_slots_accept_hole_sentinel():
    values=json.loads(WIRE_SPECIAL)
    values[0]['_-1']=2
    r=inspect_native_loader_state(html(enqueue(json.dumps(values))),URL)
    assert r['decoded_loader_state_count']==0
    assert_held(r)


def test_literal_nonfinite_json_is_still_rejected_not_repaired():
    for raw in ('NaN','Infinity','-Infinity','1e999'):
        body=direct().replace(b'"DO_NOT_PRINT"',raw.encode())
        r=inspect_native_loader_state(body,URL)
        assert r['status']=='nonfinite_json' and not r['decoded_loader_state_count']
