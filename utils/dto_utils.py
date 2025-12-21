from typing import List

from models import TestCategory
from schemas.test_category_schema import TestCategoryDTO

# map testcategory list to dto list
def map_TestCategoryListEntity_to_dtoList(categories : List[TestCategory]) -> List[TestCategoryDTO]:
    list = []
    dto = TestCategoryDTO()
    for category in categories:
        dto.id = category.id
        dto.name = category.name
        dto.description = category.description
        dto.category_type = category.category_type
        list.append(dto)

    return list