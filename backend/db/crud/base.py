from typing import Dict, List

from sqlalchemy import (Delete, Select, Update, and_, delete, func, select,
                        update)


class BaseRetrieveMixin:
    @classmethod
    def _exists(cls, filters: list = None, **kwargs) -> Select:
        """Build and return exists DB query"""

        base_query = select(func.count(1)).select_from(cls)
        if kwargs:
            base_query = base_query.filter_by(**kwargs)
        if filters:
            base_query = base_query.where(and_(*filters))
        return base_query

    @classmethod
    def _get_one(cls, fields: list = None, filters: list = None, **kwargs) -> Select:
        """Build and return DB query for getting one instance"""
        base_query = (
            select(cls)
            if not fields
            else select(*[getattr(cls, field) for field in fields])
        )
        if kwargs:
            base_query = base_query.filter_by(**kwargs)
        if filters:
            base_query = base_query.where(*filters)
        return base_query

    @classmethod
    def _get_all(
        cls, fields: list = None, filters: list = None, order_by: list = None, **kwargs
    ) -> Select:
        """Build and return DB query for getting all instances"""
        base_query = (
            select(cls)
            if not fields
            else select(*[getattr(cls, field) for field in fields])
        )
        if kwargs:
            base_query = base_query.filter_by(**kwargs)
        if filters:
            base_query = base_query.where(*filters)
        if order_by:
            base_query = base_query.order_by(*order_by)
        return base_query


class BaseUpdateMixin:
    @classmethod
    def _update(cls, new_data: Dict, filters: List = None, **kwargs) -> Update:
        """Build and return DB query for updating one instance"""
        base_query = update(cls)
        if kwargs:
            base_query = base_query.filter_by(**kwargs)
        if filters:
            base_query = base_query.where(*filters)
        return base_query.values(**new_data)


class BaseDeleteMixin:
    @classmethod
    def _delete(cls, filters: list = None, **kwargs) -> Delete:
        """Build and return DB query for deleting one instance"""
        base_query = delete(cls)
        if filters:
            base_query = base_query.where(*filters)
        if kwargs:
            base_query = base_query.filter_by(**kwargs)
        return base_query


class BaseCRUD(BaseRetrieveMixin, BaseUpdateMixin, BaseDeleteMixin):
    @classmethod
    def exists(cls, filters: list = None, **kwargs) -> Select:
        """Execute DB query and return Bool val"""
        return super()._exists(filters=filters, **kwargs)

    @classmethod
    def get_one(cls, fields: list = None, filters: list = None, **kwargs) -> Select:
        """Execute DB query and return one instance or None"""
        return super()._get_one(fields=fields, filters=filters, **kwargs)

    @classmethod
    def get_all(
        cls, fields: list = None, filters: list = None, order_by: list = None, **kwargs
    ) -> Select:
        """Build and return DB query for getting all instances"""
        return super()._get_all(
            fields=fields, filters=filters, order_by=order_by, **kwargs
        )

    @classmethod
    def update(cls, new_data: Dict, filters: List = None, **kwargs) -> Update:
        """Execute DB query for updating one Instance"""
        return super()._update(filters=filters, new_data=new_data, **kwargs)

    @classmethod
    def delete(cls, filters: list = None, **kwargs) -> Delete:
        """Execute DB query and delete one Instance"""
        return super()._delete(filters=filters, **kwargs)
