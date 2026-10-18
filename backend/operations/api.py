from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import Membership
from .models import Customer, ServiceOrder, Case, WorkflowStage, CaseEvent


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'kind', 'name', 'phone', 'email', 'country', 'address', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrder
        fields = ['id', 'reference', 'customer', 'status', 'description', 'currency', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ['id', 'reference', 'order', 'customer', 'template', 'status', 'current_stage', 'assigned_to', 'created_at']
        read_only_fields = fields


def membership_for(request, slug, roles=None):
    queryset = Membership.objects.select_related('organization').filter(user=request.user, organization__slug=slug)
    if roles:
        queryset = queryset.filter(role__in=roles)
    return get_object_or_404(queryset)


class CustomerListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        member = membership_for(request, slug)
        records = Customer.objects.filter(organization=member.organization).order_by('-created_at')[:100]
        return Response(CustomerSerializer(records, many=True).data)

    def post(self, request, slug):
        member = membership_for(request, slug, ['owner', 'manager'])
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(organization=member.organization)
        return Response(CustomerSerializer(obj).data, status=status.HTTP_201_CREATED)


class OrderListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        member = membership_for(request, slug)
        orders = ServiceOrder.objects.filter(organization=member.organization).order_by('-created_at')[:100]
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request, slug):
        member = membership_for(request, slug, ['owner', 'manager'])
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = get_object_or_404(Customer, id=serializer.validated_data['customer'].id, organization=member.organization)
        obj = serializer.save(organization=member.organization, customer=customer, created_by=request.user)
        return Response(OrderSerializer(obj).data, status=status.HTTP_201_CREATED)


class CaseList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        member = membership_for(request, slug)
        cases = Case.objects.filter(organization=member.organization).order_by('-created_at')[:100]
        return Response(CaseSerializer(cases, many=True).data)


class AdvanceCase(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, slug, case_id):
        member = membership_for(request, slug, ['owner', 'manager'])
        case = get_object_or_404(Case.objects.select_for_update(), id=case_id, organization=member.organization)
        if case.status != 'open':
            return Response({'detail': 'Only open cases can advance'}, status=409)
        stages = list(WorkflowStage.objects.filter(template=case.template).order_by('position'))
        current_index = next((i for i, stage in enumerate(stages) if stage.id == case.current_stage_id), -1)
        next_index = current_index + 1
        if next_index >= len(stages):
            return Response({'detail': 'No further stage'}, status=409)
        next_stage = stages[next_index]
        if next_stage.requires_approval:
            return Response({'detail': 'Stage requires separate approval; cannot auto-advance'}, status=409)
        case.current_stage = next_stage
        case.save(update_fields=['current_stage'])
        CaseEvent.objects.create(case=case, stage=next_stage, actor=request.user, comment=str(request.data.get('comment', ''))[:2000])
        return Response(CaseSerializer(case).data)