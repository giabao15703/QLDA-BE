#!/bin/sh

# Master data

python manage.py loaddata data/auction_type.yaml data/contract_type.yaml data/countries.yaml data/country_states.yaml
python manage.py loaddata data/number_of_employee.yaml data/payment_term.yaml data/currency.yaml data/delivery_term.yaml data/gender.yaml
python manage.py loaddata data/technical_weighting.yaml data/unit_of_measure.yaml
python manage.py loaddata data/family_code.yaml data/cluster_code.yaml data/sub_cluster_code.yaml data/category.yaml
python manage.py loaddata data/level.yaml data/position.yaml
python manage.py loaddata data/industry.yaml
python manage.py loaddata data/client_focus.yaml
python manage.py loaddata data/language.yaml
python manage.py loaddata data/reason.yaml
python manage.py loaddata data/industry_cluster.yaml
python manage.py loaddata data/industry_sectors.yaml
python manage.py loaddata data/industry_sub_sectors.yaml
python manage.py loaddata data/supplier_list.yaml
python manage.py loaddata data/sicp_registration.yaml
python manage.py loaddata data/exchange_rate.yaml

python manage.py loaddata data/bank.yaml
python manage.py loaddata data/email_templates.yaml

# Sale schema

python manage.py loaddata data/profile_features_buyer.yaml
python manage.py loaddata data/profile_features_supplier.yaml
python manage.py loaddata data/auction_fee.yaml
python manage.py loaddata data/platform_fee.yaml

# Banner
python manage.py loaddata data/banner.yaml


# Translation
python manage.py loaddata data/delivery_term_translation.yaml
python manage.py loaddata data/payment_term_translation.yaml
python manage.py loaddata data/position_translation.yaml
python manage.py loaddata data/reason_translation.yaml
python manage.py loaddata data/industry_translation.yaml
python manage.py loaddata data/industry_cluster_translation.yaml
python manage.py loaddata data/industry_sectors_translation.yaml
python manage.py loaddata data/industry_sub_sectors_translation.yaml
python manage.py loaddata data/family_code_translation.yaml
python manage.py loaddata data/cluster_code_translation.yaml
python manage.py loaddata data/sub_cluster_code_translation.yaml
python manage.py loaddata data/category_translation.yaml
python manage.py loaddata data/currency_translation.yaml
python manage.py loaddata data/gender_translation.yaml
python manage.py loaddata data/unit_of_measure_translation.yaml
python manage.py loaddata data/technical_weighting_translation.yaml
python manage.py loaddata data/client_focus_translation.yaml
python manage.py loaddata data/email_templates_translation.yaml
python manage.py loaddata data/email_templates_translation_2.yaml


#Master admin
python manage.py loaddata data/master_admin.yaml