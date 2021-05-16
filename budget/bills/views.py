import copy

# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.db.transaction import atomic, savepoint, savepoint_rollback
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bill, BillItem, Category, Catelog
from .serializers import BillSerializer, BillItemSerializer, CategorySerializer, CatelogSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class BillList(APIView):
    def get(self, request, format=None):
        bills = Bill.objects.all()
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)

    @atomic
    def post(self, request, format=None):
        seralizer = BillSerializer(data=request.data)
        if seralizer.is_valid():
            seralizer.save()
            return Response(seralizer.data, status=status.HTTP_201_CREATED)
        return Response(seralizer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillDetail(APIView):
    def get_object(self, pk):
        try:
            return Bill.objects.get(pk=pk)
        except Bill.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        bill = self.get_object(pk)
        seralizer = BillSerializer(bill)
        return Response(seralizer.data)

    def put(self, request, pk, format=None):
        bill = self.get_object(pk)
        serializer = BillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        bill = self.get_object(pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BillItemList(APIView):
    @atomic
    def post(self, request, pk, format=None):
        save_before = savepoint()
        try:
            data = copy.deepcopy(request.data)
            for item in data:
                item['bill_id'] = pk
            seralizer = BillItemSerializer(data=data, many=True)
            if seralizer.is_valid():
                seralizer.save()
                for obj, item in zip(seralizer.data, data):
                    # handle categories
                    if ('categories' in item) and isinstance(item['categories'], list) and len(item['categories']) > 0:
                        categories = item['categories']
                        for category in categories:
                            if Category.objects.filter(category=category).exists():
                                cat = Category.objects.filter(
                                    category=category)[0]
                                catelog = {}
                                catelog['item_id'] = obj['id']
                                catelog['category_id'] = cat.id
                                catelog_serializer = CatelogSerializer(
                                    data=catelog)
                                if catelog_serializer.is_valid():
                                    catelog_serializer.save()
                                else:
                                    raise catelog_serializer.errors
                            else:
                                # create a new category
                                category_serializer = CategorySerializer(
                                    data={'category': category})
                                if category_serializer.is_valid():
                                    category_serializer.save()
                                    catelog = {}
                                    catelog['item_id'] = obj['id']
                                    catelog['category_id'] = category_serializer.data['id']
                                    catelog_serializer = CatelogSerializer(
                                        data=catelog)
                                    if catelog_serializer.is_valid():
                                        catelog_serializer.save()
                                    else:
                                        raise catelog_serializer.errors
                                else:
                                    raise category_serializer.errors
                return Response(seralizer.data, status=status.HTTP_201_CREATED)
            # return Response(seralizer.errors, status=status.HTTP_400_BAD_REQUEST)
            raise seralizer.errors
        except Exception as e:
            savepoint_rollback(save_before)
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        items = BillItem.objects.filter(bill_id=pk)
        seralizer = BillItemSerializer(items, many=True)
        return Response(seralizer.data)


class AllBillItemList(APIView):
    def get(self, request, format=None):
        items = BillItem.objects.all()
        seralizer = BillItemSerializer(items, many=True)
        return Response(seralizer.data, status=status.HTTP_200_OK)


class BillItemDetail(APIView):
    def get_object(self, pk):
        try:
            return BillItem.objects.get(pk=pk)
        except BillItem.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        item = self.get_object(pk)
        serializer = BillItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        item = self.get_object(pk)
        serializer = BillItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryList(APIView):
    def post(self, request, format=None):
        seralizer = CategorySerializer(data=request.data)
        if seralizer.is_valid():
            seralizer.save()
            return Response(seralizer.data, status=status.HTTP_201_CREATED)
        return Response(seralizer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CategoryDetail(APIView):
    def get_category(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        cat = self.get_category(pk)
        serializer = CategorySerializer(cat)
        return Response(serializer.data)


class BillItemCategoryList(APIView):
    @atomic
    def post(self, request, pk, format=None):
        # check bill item
        if not BillItem.objects.filter(pk=pk).exists():
            return Response(data={'error': 'Bill item [' + str(pk) + '] doesn\'t exist'}, status=status.HTTP_400_BAD_REQUEST)
        # # get current categories of the bill item
        # c_catelogs = Catelog.objects.filter(item_id=pk)
        # c_category_names = [
        #     catelog.category.category for catelog in c_catelogs]
        # # get request categories
        # r_category_names = [category['category'] for category in request.data]
        # r_category_names_set = set(r_category_names)
        # if len(r_category_names) != len(r_category_names_set):
        #     return Response(data={'error': 'Please remove duplication categories.'}, status=status.HTTP_400_BAD_REQUEST)
        # # get the categories to create
        # diff_categories = list(r_category_names_set - set(c_category_names))
        # diff_categories_dict = [{'category': category}
        #                         for category in diff_categories]
        # an array of categories
        # seralizer = CategorySerializer(data=diff_categories_dict, many=True)
        seralizer = CategorySerializer(data=request.data, many=True)
        if seralizer.is_valid():
            seralizer.save()
            # bind bill item with this category
            categories = copy.deepcopy(seralizer.data)
            catelogs = []
            for cat in categories:
                catelog = {}
                catelog['item_id'] = pk
                catelog['category_id'] = cat['id']
                catelogs.append(catelog)
            cat_serializer = CatelogSerializer(data=catelogs, many=True)
            if cat_serializer.is_valid():
                cat_serializer.save()
                return Response(cat_serializer.data, status=status.HTTP_200_OK)
            return Response(cat_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(seralizer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        # check bill item
        if not BillItem.objects.filter(pk=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        catelogs = Catelog.objects.filter(item_id=pk)
        categories_id = [catelog.category_id for catelog in catelogs]
        categories = Category.objects.filter(pk__in=categories_id)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @atomic
    def delete(self, request, pk, format=None):
        # check bill item
        if not BillItem.objects.filter(pk=pk).exists():
            return Response(data={'error': 'Bill item doesn\'t exist'}, status=status.HTTP_400_BAD_REQUEST)
        # ensure all deletions exist
        catelogs = Catelog.objects.filter(item_id=pk)
        categories_set = set(
            [catelog.category.category for catelog in catelogs])
        categories_to_delete_set = set(request.data)
        if not categories_to_delete_set.issubset(categories_set):
            return Response(data=list(categories_to_delete_set), status=status.HTTP_400_BAD_REQUEST)
        # save point
        save_point = savepoint()
        try:
            for category in request.data:
                category = Category.objects.filter(category=category)
                category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            savepoint_rollback(savepoint)
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
