from typing import Any

from mcp.server import MCPServer

from database import (
    filter_sales as db_filter_sales,
    summarize_sales as db_summarize_sales,
)
from security import (
    rate_limiter,
    sanitize_filter_text,
    validate_limit,
)


# MCP server structure adapted from the official MCP Python SDK documentation:
# https://github.com/modelcontextprotocol/python-sdk
#
# The tool and prompt logic below is specific to this assignment.

mcp = MCPServer("Kezia Sales Analytics")


@mcp.tool()
def filter_sales(
    region: str | None = None,
    category: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Filter individual sales records by optional region and category.

    Args:
        region: Optional region such as North, South, East, or West.
        category: Optional category such as Electronics or Furniture.
        limit: Maximum number of records to return, from 1 to 100.

    Returns:
        A dictionary containing matching sales records or a safe error message.
    """

    try:
        # Best practice 1: rate limiting
        rate_limiter.check("filter_sales")

        # Best practice 2: input sanitization
        clean_region = sanitize_filter_text(
            region,
            "region",
        )

        clean_category = sanitize_filter_text(
            category,
            "category",
        )

        clean_limit = validate_limit(limit)

        results = db_filter_sales(
            region=clean_region,
            category=clean_category,
            limit=clean_limit,
        )

        return {
            "success": True,
            "count": len(results),
            "filters": {
                "region": clean_region,
                "category": clean_category,
                "limit": clean_limit,
            },
            "results": results,
        }

    except ValueError as error:
        return {
            "success": False,
            "error": str(error),
        }


@mcp.tool()
def sales_summary(
    group_by: str = "region",
) -> dict[str, Any]:
    """
    Summarize sales by region, category, or product.

    Args:
        group_by: Group results by region, category, or product.

    Returns:
        Aggregated units and revenue or a safe error message.
    """

    try:
        # Best practice 1: rate limiting
        rate_limiter.check("sales_summary")

        # Sanitize text before it reaches the database layer
        clean_group_by = sanitize_filter_text(
            group_by,
            "group_by",
        )

        if clean_group_by is None:
            clean_group_by = "region"

        results = db_summarize_sales(clean_group_by)

        return {
            "success": True,
            "group_by": clean_group_by,
            "count": len(results),
            "results": results,
        }

    except ValueError as error:
        return {
            "success": False,
            "error": str(error),
        }


@mcp.prompt()
def analyze_sales(
    focus: str = "overall sales performance",
) -> str:
    """
    Generate a structured prompt for analyzing the sales dataset.
    """

    try:
        clean_focus = sanitize_filter_text(
            focus,
            "focus",
            max_length=100,
        )
    except ValueError:
        clean_focus = "overall sales performance"

    if clean_focus is None:
        clean_focus = "overall sales performance"

    return f"""
Analyze the available sales dataset with a focus on {clean_focus}.

Use the MCP sales tools when appropriate:

1. Use filter_sales when you need individual sales records filtered
   by region or category.

2. Use sales_summary when you need aggregated sales performance
   grouped by region, category, or product.

In your analysis:

- Identify important sales patterns.
- Compare stronger and weaker segments.
- Discuss both units sold and revenue where relevant.
- Base all numerical conclusions on data returned by the tools.
- Do not invent sales values or facts that are not present in the data.
- Mention relevant limitations of the dataset.

Provide a concise and clearly structured analysis.
""".strip()