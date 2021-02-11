# -*- coding: utf-8 -*-
import anthem


@anthem.log
def main(ctx):
    ctx.env.cr.execute("""
        ALTER TABLE IF EXISTS delivery_project RENAME COLUMN sale_order_id \
        TO order_id;
        ALTER TABLE IF EXISTS delivery_project RENAME TO delivery_project_so;
        ALTER TABLE IF EXISTS delivery_project_line rename to delivery_line_so;
        UPDATE mail_message set model = 'delivery.project.so' \
        where model = 'delivery.project';
        UPDATE ir_attachment set res_model = 'delivery.project.so' \
        where res_model = 'delivery.project';
        UPDATE mail_followers set res_model = 'delivery.project.so' \
        where res_model = 'delivery.project';
    """)
