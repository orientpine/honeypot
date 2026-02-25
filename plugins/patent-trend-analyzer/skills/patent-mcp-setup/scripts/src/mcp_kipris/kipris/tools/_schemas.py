"""[GJ] Common Pydantic schemas for tool parameter validation.

Eliminates duplicated field definitions across 15 tool files.
"""

from pydantic import BaseModel, Field, field_validator

from mcp_kipris.kipris.tools.code import country_dict, sort_field_dict


class KoreanSearchMixin(BaseModel):
    """[GJ] Common parameters for Korean patent search tools."""

    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10, range is 1-30")
    patent: bool = Field(True, description="Include patents, default is True")
    utility: bool = Field(True, description="Include utility models, default is True")
    lastvalue: str = Field(
        "",
        description="Patent registration status; leave empty for all, (A, C, F, G, I, J, R or empty)",
    )
    sort_spec: str = Field(
        "AD",
        description=(
            "Field to sort by; default is 'AD' "
            "(PD-공고일자, AD-출원일자, GD-등록일자, OPD-공개일자, "
            "FD-국제출원일자, FOD-국제공개일자, RD-우선권주장일자)"
        ),
    )
    desc_sort: bool = Field(
        True,
        description="Sort in descending order; default is True (latest date first).",
    )


class ForeignSearchMixin(BaseModel):
    """[GJ] Common parameters for Foreign patent search tools."""

    current_page: int = Field(1, description="Current page number")
    sort_field: str = Field("AD", description="Sort field")
    sort_state: bool = Field(True, description="Sort state (descending if True)")
    collection_values: str = Field(
        "US",
        description=(
            "Collection values, must be one of: "
            "US(미국), EP(유럽), WO(PCT), JP(일본), PJ(일본영문초록), "
            "CP(중국), CN(중국특허영문초록), TW(대만영문초록), RU(러시아), "
            "CO(콜롬비아), SE(스웨덴), ES(스페인), IL(이스라엘)"
        ),
    )

    @field_validator("collection_values")
    @classmethod
    def validate_collection_values(cls, v: str) -> str:
        if v not in country_dict:
            raise ValueError(f"collection_values must be one of: {', '.join(country_dict.keys())}")
        return v

    @field_validator("sort_field")
    @classmethod
    def validate_sort_field(cls, v: str) -> str:
        if v not in sort_field_dict:
            raise ValueError(f"sort_field must be one of: {', '.join(sort_field_dict.keys())}")
        return v


class BatchExportMixin(BaseModel):
    """[GJ] Common parameters for batch export tools."""

    max_results: int = Field(200, description="최대 검색 결과 수 (기본값: 200, 최대: 1000)")
    output_format: str = Field("excel", description="출력 형식 (excel 또는 markdown)")

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        if v not in ["excel", "markdown"]:
            raise ValueError("output_format must be 'excel' or 'markdown'")
        return v
