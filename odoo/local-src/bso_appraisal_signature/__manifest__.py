{
    'name': 'Appraisal Signature',
    'category': 'Appraisals',
    'description': 'Agree and sign the content for a survey answer',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['web_widget_digitized_signature', 'hr_appraisal',
                'survey', 'web'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/survey_user_input_view.xml',
        'views/hr_appraisal_search_view.xml',
    ],
    'application': False,
}
