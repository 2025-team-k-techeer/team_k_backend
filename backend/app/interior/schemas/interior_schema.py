from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InteriorTypeQuery(BaseModel):
    # The leading underscore is intentional to match the database field name.
    _id: str
    name: str


# class FurnitureNameQuery(BaseModel):
#     _id: str
#     style_name: str
#     profile_image_url: Optional[str]
#     updated_at: datetime
class InteriorTypeResponse(BaseModel):
    """
    urnitureStyleResponse represents the schema for a furniture style response.

    Attributes:
            _id (str): The unique identifier for the furniture style.
            style_description (str): A description of the furniture style.
            style_name (str): The name of the furniture style.
            example_image_url_image_url (Optional[str]): An optional URL pointing to an example image of the furniture style.
    """

    _id: str
    description: str
    name: str
    example_image_url: Optional[str]
