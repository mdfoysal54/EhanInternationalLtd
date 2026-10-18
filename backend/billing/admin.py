from django.contrib import admin
from .models import PostingLink, Allocation, Expense, Refund, TaxCode, BankStatementLine
for model in (PostingLink,Allocation,Expense,Refund,TaxCode,BankStatementLine):
    admin.site.register(model)