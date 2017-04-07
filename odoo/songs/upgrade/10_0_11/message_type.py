import anthem


@anthem.log
def update_message_type(ctx):
    for state in ('confirmed', 'approved', 'done'):
        ctx.env.ref('purchase.mt_rfq_%s' % state).default = True


@anthem.log
def main(ctx):
    update_message_type(ctx)
