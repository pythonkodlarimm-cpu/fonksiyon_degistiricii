# -*- coding: utf-8 -*-

def __getattr__(name):
    if name == "GelistiriciModYoneticisi":
        from app.ui.dosya_secici_paketi.gelistirici_mod.yoneticisi import GelistiriciModYoneticisi
        return GelistiriciModYoneticisi
    raise AttributeError(name)


__all__ = ["GelistiriciModYoneticisi"]
