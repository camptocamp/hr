-- fix hr_contract_type xmlids
UPDATE ir_model_data SET module = 'BSO_hr' WHERE module = 'hr_contract' AND model = 'hr.contract.type' AND name ~ '^hr_contract_type_0[0-9][0-9]$';
-- set sequence on invoice report
UPDATE ir_ui_view SET priority = 99 WHERE type = 'qweb' AND name = 'report_invoice_document_inherit_sale_specific';
-- fix manual csv import of account_account on existing modules
update ir_model_data set module=module||'_import' where id in (select id from ir_model_data where model='account.account' and res_id in (select id from account_account where create_uid=107 order by company_id) and module != '');
