#!/usr/bin/env python3
from __future__ import annotations
import copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'schemas'/'portable'; OUT.mkdir(parents=True,exist_ok=True)
DRAFT='https://json-schema.org/draft/2020-12/schema'

def obj(required, props, *, additional=False):
    return {'type':'object','required':required,'properties':props,'additionalProperties':additional}
def arr(items): return {'type':'array','items':items}
def nullable(schema): return {'anyOf':[schema,{'type':'null'}]}
ID={'type':'string','minLength':3,'maxLength':512,'pattern':r'^\S+:\S+$'}
TERM=copy.deepcopy(ID)
DIGEST={'type':'string','pattern':'^[0-9a-f]{64}$'}
TIME={'type':'string','format':'date-time'}
CONF={'type':'number','minimum':0,'maximum':1}
JSON={}
PRIV=obj(['sensitivity','access_tier','disposition'],{
 'sensitivity':{'enum':['public','personal','sensitive_personal','restricted','unknown']},
 'access_tier':{'enum':['public','research','restricted','embargoed']},
 'disposition':{'enum':['publish','publish_metadata_only','withhold','needs_review']},
 'reason_codes':arr({'type':'string'}),'assessed_by':ID,'human_reviewed':{'type':'boolean'}})
POS=obj(['source','partition','sequence'],{'source':ID,'partition':{'type':'string','minLength':1},'sequence':{'type':'integer','minimum':0}})
TEMP=obj(['timestamp'],{'timestamp':TIME,'precision':{'enum':['second','minute','hour','day','month','year','unknown']},'source_timezone':{'type':'string'},'uncertainty_seconds':{'type':'integer','minimum':0},'source_text':{'type':'string'}})
LOC=obj([],{'uri':{'type':'string','format':'uri'},'warc_record_id':{'type':'string'},'wacz_path':{'type':'string'},'blob_path':{'type':'string'}})
BBOX=obj(['page','x','y','width','height'],{'page':{'type':'integer','minimum':1},'x':{'type':'number'},'y':{'type':'number'},'width':{'type':'number','minimum':0},'height':{'type':'number','minimum':0},'coordinate_system':{'type':'string'}})
SELECTOR={'oneOf':[
 obj(['selector_type','start','end'],{'selector_type':{'const':'bytes'},'start':{'type':'integer','minimum':0},'end':{'type':'integer','minimum':0}}),
 obj(['selector_type','span'],{'selector_type':{'const':'text'},'span':obj(['start','end'],{'start':{'type':'integer','minimum':0},'end':{'type':'integer','minimum':0}})}),
 obj(['selector_type','page'],{'selector_type':{'const':'page'},'page':{'type':'integer','minimum':1}}),
 obj(['selector_type','bbox'],{'selector_type':{'const':'bounding_box'},'bbox':BBOX}),
 obj(['selector_type','pointer'],{'selector_type':{'const':'json_pointer'},'pointer':{'type':'string'}}),
 obj(['selector_type'],{'selector_type':{'const':'warc_payload'}}),]}
EREF=obj(['evidence_id'],{'evidence_id':ID,'selector':SELECTOR,'role':TERM})
EVID=obj(['schema_version','evidence_id','logical_record_id','revision','source_kind','media_type','locator','content_sha256','captured_at','privacy'],{
 'schema_version':{'type':'string'},'evidence_id':ID,'logical_record_id':ID,'revision':{'type':'integer','minimum':1},'source_kind':TERM,'media_type':{'type':'string'},'locator':LOC,'content_sha256':DIGEST,'byte_length':{'type':'integer','minimum':0},'captured_at':TIME,'source_time':TEMP,'privacy':PRIV,'attributes':{'type':'object'}})
EOLINK=obj(['object_id','object_type','qualifier'],{'object_id':ID,'object_type':TERM,'qualifier':TERM})
PROV=obj(['producer','producer_version'],{'producer':ID,'producer_version':{'type':'string'},'software_commit':{'type':'string'},'run_id':ID,'input_ids':arr(ID),'parameters':{'type':'object'}})
EVENT=obj(['schema_version','event_id','logical_event_id','revision','operation','site','jurisdiction','case_id','activity','observed_at','captured_at','processed_at','position','assertion_status','provenance','privacy'],{
 'schema_version':{'type':'string'},'event_id':ID,'logical_event_id':ID,'revision':{'type':'integer','minimum':1},'operation':{'enum':['upsert','retract']},'site':ID,'jurisdiction':TERM,'case_id':ID,'activity':TERM,'event_time':TEMP,'observed_at':TIME,'captured_at':TIME,'processed_at':TIME,'position':POS,'assertion_status':{'enum':['observed','candidate','inferred','asserted','human_certified','unknown']},'confidence':CONF,'objects':arr(EOLINK),'evidence':arr(EREF),'document_signal_ids':arr(ID),'rule_result_ids':arr(ID),'supersedes_event_id':ID,'retracts_event_id':ID,'correlation_id':ID,'causation_id':ID,'provenance':PROV,'privacy':PRIV,'attributes':{'type':'object'}})
OBJECT=obj(['schema_version','object_id','object_type','privacy'],{'schema_version':{'type':'string'},'object_id':ID,'object_type':TERM,'privacy':PRIV,'attributes':{'type':'object'},'evidence':arr(EREF)})
MODEL=obj(['name','version'],{'name':{'type':'string'},'version':{'type':'string'},'runtime':{'type':'string'},'model_sha256':DIGEST,'license':{'type':'string'}})
SEG=obj(['segment_id','reading_order','text_sha256','character_count','privacy'],{'segment_id':ID,'reading_order':{'type':'integer','minimum':0},'text_sha256':DIGEST,'character_count':{'type':'integer','minimum':0},'text_blob_id':ID,'inline_text':{'type':'string'},'bbox':BBOX,'confidence':CONF,'language':{'type':'string'},'privacy':PRIV})
PAGE=obj(['page_number','page_sha256','width','height','extraction_method'],{'page_number':{'type':'integer','minimum':1},'page_sha256':DIGEST,'width':{'type':'number','exclusiveMinimum':0},'height':{'type':'number','exclusiveMinimum':0},'extraction_method':{'enum':['born_digital','ocr','hybrid','manual']},'model':MODEL,'quality_score':CONF,'warnings':arr({'type':'string'}),'segments':arr(SEG)})
DOC=obj(['schema_version','document_id','source_evidence_id','source_sha256','media_type','created_at','extractor','pages','privacy'],{'schema_version':{'type':'string'},'document_id':ID,'source_evidence_id':ID,'source_sha256':DIGEST,'media_type':{'type':'string'},'created_at':TIME,'extractor':MODEL,'pages':arr(PAGE),'privacy':PRIV,'attributes':{'type':'object'}})
SIG=obj(['schema_version','signal_id','signal_type','assertion_status','document_id','producer','privacy'],{'schema_version':{'type':'string'},'signal_id':ID,'signal_type':TERM,'assertion_status':{'enum':['observed','candidate','inferred','asserted','human_certified','unknown']},'confidence':CONF,'document_id':ID,'evidence':arr(EREF),'proposed_activity':TERM,'extracted_values':{'type':'object'},'producer':MODEL,'privacy':PRIV})
REVIEW=obj(['schema_version','review_id','subject_id','reviewer_id','profile_id','reviewed_at','decision','previous_status','resulting_status'],{'schema_version':{'type':'string'},'review_id':ID,'subject_id':ID,'reviewer_id':ID,'profile_id':ID,'reviewed_at':TIME,'decision':{'enum':['confirm','correct','reject','defer','escalate']},'previous_status':{'enum':['observed','candidate','inferred','asserted','human_certified','unknown']},'resulting_status':{'enum':['observed','candidate','inferred','asserted','human_certified','unknown']},'evidence':arr(EREF),'rationale':{'type':'string'},'corrected_values':{'type':'object'}})
FINDING=obj(['rule_id','layer','severity','message'],{'rule_id':TERM,'layer':{'enum':['structural','semantic','process','statutory','privacy','data_quality']},'severity':{'enum':['info','warning','review_needed','error','critical']},'message':{'type':'string'},'subject_id':ID,'evidence':arr(EREF),'requires_human_review':{'type':'boolean'},'details':{'type':'object'}})
TRACE_STEP=obj(['step_id','kind','label'],{'step_id':ID,'kind':{'enum':['input','evidence_check','calculation','decision','process_constraint','notice','external_reference']},'label':{'type':'string'},'input_ids':arr(ID),'output_ids':arr(ID),'evidence':arr(EREF),'details':{'type':'object'}})
TRACE=obj(['schema_version','trace_id','case_id','profile_id','engine_id','engine_version','created_at','assertion_status','steps','findings'],{'schema_version':{'type':'string'},'trace_id':ID,'case_id':ID,'profile_id':ID,'engine_id':ID,'engine_version':{'type':'string'},'created_at':TIME,'assertion_status':{'enum':['observed','candidate','inferred','asserted','human_certified','unknown']},'steps':arr(TRACE_STEP),'findings':arr(FINDING)})
CHK=obj(['schema_version','checkpoint_id','consumer','created_at','partitions'],{'schema_version':{'type':'string'},'checkpoint_id':ID,'consumer':ID,'created_at':TIME,'partitions':arr(obj(['source','partition','last_sequence'],{'source':ID,'partition':{'type':'string'},'last_sequence':{'type':'integer','minimum':0},'watermark':TIME})),'state_hash':DIGEST,'attributes':{'type':'object'}})
DELTA=obj(['schema_version','delta_id','logical_record_id','revision','operation','site','jurisdiction','position','observed_at','captured_at'],{'schema_version':{'type':'string'},'delta_id':ID,'logical_record_id':ID,'revision':{'type':'integer','minimum':1},'operation':{'enum':['upsert','delete','recapture','repair']},'site':ID,'jurisdiction':TERM,'position':POS,'observed_at':TIME,'captured_at':TIME,'previous_content_sha256':DIGEST,'current_content_sha256':DIGEST,'evidence':EVID,'request_hint':ID,'supersedes_delta_id':ID,'correlation_id':ID,'causation_id':ID,'attributes':{'type':'object'}})
BUNDLE=obj(['schema_version'],{'schema_version':{'type':'string'},'evidence':arr(EVID),'objects':arr(OBJECT),'object_links':arr({'type':'object'}),'object_changes':arr({'type':'object'}),'document_signals':arr(SIG),'events':arr(EVENT),'findings':arr(FINDING),'human_reviews':arr(REVIEW),'checkpoint':CHK})
RECORDSNAP=obj(['logical_record_id','revision','last_delta_id'],{'logical_record_id':ID,'revision':{'type':'integer','minimum':1},'current_digest':DIGEST,'last_delta_id':ID,'last_event_id':ID})
REPLAYSNAP=obj(['schema_version','snapshot_id','consumer','created_at','records','partitions','state_hash'],{'schema_version':{'type':'string'},'snapshot_id':ID,'consumer':ID,'created_at':TIME,'records':arr(RECORDSNAP),'partitions':CHK['properties']['partitions'],'state_hash':DIGEST})
SCHEMAS={'evidence-record':EVID,'evidence-delta':DELTA,'process-event':EVENT,'document-bundle':DOC,'document-signal':SIG,'validation-finding':FINDING,'conformance-trace':TRACE,'human-review-record':REVIEW,'normalized-bundle':BUNDLE,'stream-checkpoint':CHK,'replay-snapshot':REPLAYSNAP}
# Output/result schemas kept strict at their top-level but intentionally compact.
SCHEMAS['dashboard-summary']=obj(['case_count','active_event_count','activities','edges','variants','waiting_time_histogram'],{'case_count':{'type':'integer','minimum':0},'active_event_count':{'type':'integer','minimum':0},'activities':arr({'type':'object'}),'edges':arr({'type':'object'}),'variants':arr({'type':'object'}),'waiting_time_histogram':arr({'type':'object'})})
SCHEMAS['ocel-projection']=obj(['events','objects','event_object_links','object_object_links','object_changes'],{k:arr({'type':'object'}) for k in ['events','objects','event_object_links','object_object_links','object_changes']})
SCHEMAS['public-projection']=obj(['policy_id','events','withheld_event_count','metadata_only_event_count'],{'policy_id':ID,'events':arr({'type':'object'}),'withheld_event_count':{'type':'integer','minimum':0},'metadata_only_event_count':{'type':'integer','minimum':0}})
SCHEMAS['mining-run-manifest']=obj(['schema_version','run_id','created_at','source_dataset','source_revision','software_commit','rust_version','rust4pm_version','foi_process_version','privacy_profile','inputs','outputs'],{'schema_version':{'type':'string'},'run_id':ID,'created_at':TIME,'source_dataset':ID,'source_revision':{'type':'string'},'source_manifest_sha256':DIGEST,'software_commit':{'type':'string'},'rust_version':{'type':'string'},'rust4pm_version':{'type':'string'},'foi_process_version':{'type':'string'},'parameters':{'type':'object'},'privacy_profile':PRIV,'inputs':arr({'type':'object'}),'outputs':arr({'type':'object'}),'sbom_artifact_id':ID,'environment':{'type':'object'}})
for name,schema in SCHEMAS.items():
    document={'$schema':DRAFT,'$id':f'https://w3id.org/foi-process/schema/{name}.schema.json','title':name.replace('-',' ').title(),**schema}
    (OUT/f'{name}.schema.json').write_text(json.dumps(document,indent=2)+"\n")
print(f'wrote {len(SCHEMAS)} portable schemas')
