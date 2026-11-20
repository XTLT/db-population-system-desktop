from .._imports import *
from .._consts import *
from ..funcs import *

_HEADERS = None
_LOCAL_MODULES = None
_to_amount = None

class SubsidySummaryDialogQueryLocalMixin:
    def _query_local(self):
        from core.database import (
            DibaoPayment,
            DisabilityCarePayment,
            ElderlyAllowance,
            LandSubsidy,
            PensionInsurance,
            TekunPayment,
            get_session,
        )

        model_map = {
            "dibao_payment": DibaoPayment,
            "elderly_allowance": ElderlyAllowance,
            "land_subsidy": LandSubsidy,
            "disability_care_payment": DisabilityCarePayment,
            "pension_insurance": PensionInsurance,
            "tekun_payment": TekunPayment,
        }

        records = []
        by_module = []
        session = get_session()
        try:
            for module, label, period_attr, amount_attr in _LOCAL_MODULES:
                model = model_map[module]
                rows = session.query(model).filter(model.id_card == self.id_card).all()
                total = 0.0
                for r in rows:
                    period = getattr(r, period_attr, "") or ""
                    amount = getattr(r, amount_attr, "") or ""
                    total += _to_amount(amount)
                    records.append({
                        "module": module,
                        "label": label,
                        "period": period,
                        "amount": amount,
                        "bank_account": getattr(r, "bank_account", "") or "",
                        "payment_status": getattr(r, "payment_status", "") or "",
                        "fail_reason": getattr(r, "fail_reason", "") or "",
                        "village": getattr(r, "village", "") or "",
                    })
                by_module.append({
                    "module": module,
                    "label": label,
                    "count": len(rows),
                    "total_amount": f"{total:.2f}" if total else "",
                })
        finally:
            session.close()

        records.sort(key=lambda x: (x["period"] or ""), reverse=True)
        return records, by_module, len(records), False
