from mapper.dto_utils import map_assessment_class_range_to_dto, map_survey_option_to_dto, map_question_to_question_dto
from schemas.test_category_schema import TestCategoryDTO


class CategoryMapper:
    @staticmethod
    def to_detailed_dto(category) -> TestCategoryDTO:

        if not category:
            return None

        dto = TestCategoryDTO()

        dto.id = category.id
        dto.name = category.name
        dto.description = category.description
        dto.category_type = category.category_type

        ranges = [map_assessment_class_range_to_dto(range) for range in category.class_ranges]
        dto.class_ranges = ranges

        options = [map_survey_option_to_dto(option) for option in category.options]

        dto.options = options

        questions = [map_question_to_question_dto(q) for q in category.questions]

        dto.questions = questions

        return dto