from dataclasses import dataclass
from typing import Sequence

from backend.optimization.db_access import (
    get_all_transfers_with_pending_status,
    get_transfer_groups,
    get_groups,
    prepare_request_structs_db,
)


@dataclass
class DataGetter:
    async def __call__(self):
        transfers = await get_all_transfers_with_pending_status()
        transfer_groups = await get_transfer_groups()
        groups = await get_groups()
        group_info, list_of_requests = prepare_request_structs_db(
            transfers, transfer_groups, groups
        )
        return group_info, list_of_requests
