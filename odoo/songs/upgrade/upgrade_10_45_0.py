# -*- coding: utf-8 -*-
import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def uninstall_module(ctx):
    """Uninstall module 'bso_chat_access_control'"""
    uninstall(ctx, ['bso_chat_access_control'])


@anthem.log
def main(ctx):
    """Applying update 10.45.0"""
    uninstall_module(ctx)
