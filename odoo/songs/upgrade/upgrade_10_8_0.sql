-- fix hr_contract_type xmlids
UPDATE ir_model_data SET module = 'BSO_hr' WHERE module = 'hr_contract' AND model = 'hr.contract.type' AND name ~ '^hr_contract_type_0[0-9][0-9]$';
-- set sequence on invoice report
UPDATE ir_ui_view SET priority = 99 WHERE type = 'qweb' AND name = 'report_invoice_document_inherit_sale_specific';
