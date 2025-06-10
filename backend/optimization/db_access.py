# Utility functions for accessing DB and preparing optimization data
from typing import Sequence

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import db_session
from backend.database.models import Group
from backend.database.models.transfer import (
    Transfer,
    transfer_group,
    GroupRole,
    TransferStatus,
)


@db_session
async def get_all_transfers_with_pending_status(db: AsyncSession) -> Sequence[Transfer]:
    result = await db.execute(
        select(Transfer).where(Transfer.status == TransferStatus.pending.value)
    )
    return result.scalars().all()


@db_session
async def get_transfer_groups(db: AsyncSession) -> Sequence:
    result = await db.execute(
        select(
            transfer_group.c.transfer_id,
            transfer_group.c.group_id,
            transfer_group.c.group_role,
        )
    )
    return result.all()


@db_session
async def get_groups(db: AsyncSession) -> Sequence[Group]:
    result = await db.execute(select(Group))
    return result.scalars().all()


def prepare_request_structs_db(
    transfers: Sequence[Transfer],
    transfer_groups: Sequence,
    groups: Sequence[Group],
):
    """Prepare group info and request list from database rows."""

    group_info = {}
    for group in groups:
        group_info[group.id] = {
            "elective_id": int(group.elective_id),
            "name": str(group.name),
            "capacity": int(group.capacity),
            "init_usage": int(getattr(group, "init_usage", 0)),
        }

    from_dict = {}
    to_dict = {}
    for row in transfer_groups:
        rid = row.request_id if hasattr(row, "request_id") else row.transfer_id
        gid = row.group_id if hasattr(row, "group_id") else row.group_id
        role = row.group_role if hasattr(row, "group_role") else row.group_role
        if role == GroupRole.FROM:
            from_dict.setdefault(rid, []).append(gid)
        elif role == GroupRole.TO:
            to_dict.setdefault(rid, []).append(gid)

    list_of_requests = []
    for transfer in transfers:
        rid = transfer.id
        list_of_requests.append(
            {
                "r_id": rid,
                "student_id": int(transfer.student_id),
                "from_elective_id": int(transfer.from_elective_id),
                "to_elective_id": int(transfer.to_elective_id),
                "priority": int(transfer.priority),
                "created_at": pd.to_datetime(transfer.created_at),
                "from_groups": from_dict.get(rid, []),
                "to_groups": to_dict.get(rid, []),
            }
        )

    return group_info, list_of_requests
