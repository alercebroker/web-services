from pydantic import BaseModel, Field
from typing import Optional, Any, Dict


class FieldValue(BaseModel):
    Valid: bool
    Float64: Optional[float] = None
    Int64: Optional[int] = None
    String: Optional[str] = None
    AnyValue: Optional[Any] = None

    def get_value(self) -> Any:
        if self.Float64 is not None:
            return self.Float64
        if self.Int64 is not None:
            return self.Int64
        if self.String is not None:
            return self.String
        if self.AnyValue is not None:
            return self.AnyValue

        raise ValueError("Field has no value")


class MetadataObject(BaseModel):
    id: str
    # Use a dictionary to store dynamic fields
    fields: Dict[str, FieldValue] = Field(default_factory=dict)

    # Custom method to handle attribute-style access
    def __getattr__(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ["id", "fields"] or name in self.__class__.model_fields:
            super().__setattr__(name, value)
        else:
            if isinstance(value, FieldValue):
                self.fields[name] = value
            else:
                raise ValueError("Value must be a FieldValue instance")

    # Class method to create from dictionary
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetadataObject":
        # Extract the id
        id_value = data["id"]

        # Create the model instance
        instance = cls(id=id_value)

        # Process dynamic fields
        for field_name, field_data in data.items():
            if field_name == "distance":
                field_value = FieldValue(Valid=True, Float64=field_data)
                instance.fields[field_name] = field_value
                continue

            if field_name == "id":
                field_value = FieldValue(Valid=True, String=field_data)
                instance.fields[field_name] = field_value
                continue

            if isinstance(field_data, dict):
                instance.fields[field_name] = FieldValue(**field_data)
                continue

            instance.fields[field_name] = FieldValue(Valid=True, AnyValue=field_data)

        return instance


class ConesearchResponse(BaseModel):
    catalog: str
    data: list[MetadataObject]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConesearchResponse":
        instance = cls(catalog=data["catalog"], data=[])
        for item in data["data"]:
            instance.data.append(MetadataObject.from_dict(item))

        return instance
