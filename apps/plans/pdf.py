from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.maps.services import build_google_maps_directions_url


def _register_fonts():
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))


def _styles():
    _register_fonts()
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="JapaneseTitle",
            parent=styles["Title"],
            fontName="HeiseiKakuGo-W5",
            fontSize=18,
            leading=24,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="JapaneseHeading",
            parent=styles["Heading2"],
            fontName="HeiseiKakuGo-W5",
            fontSize=13,
            leading=18,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="JapaneseBody",
            parent=styles["BodyText"],
            fontName="HeiseiMin-W3",
            fontSize=9,
            leading=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="JapaneseSmall",
            parent=styles["BodyText"],
            fontName="HeiseiMin-W3",
            fontSize=8,
            leading=12,
            textColor=colors.HexColor("#555555"),
        )
    )
    return styles


def _p(text, style):
    escaped = str(text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(escaped.replace("\n", "<br/>"), style)


def _section(story, title, styles):
    story.append(Spacer(1, 4 * mm))
    story.append(_p(title, styles["JapaneseHeading"]))


def _key_value_table(rows, styles):
    table = Table(
        [[_p(key, styles["JapaneseBody"]), _p(value, styles["JapaneseBody"])] for key, value in rows],
        colWidths=[35 * mm, 125 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "HeiseiMin-W3"),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f2")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d9e1dc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _amount_or_unspecified(value):
    return value if value is not None else "指定なし"


def build_travel_plan_result_pdf(result):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="AI観光プラン生成結果",
    )
    styles = _styles()
    story = []
    plan_request = result.request
    candidate_spots = plan_request.candidate_spots_snapshot or []
    directions_url = build_google_maps_directions_url(candidate_spots)

    story.append(_p("AI観光プラン生成結果", styles["JapaneseTitle"]))
    story.append(_p(plan_request.title or "旅行プラン作成依頼", styles["JapaneseBody"]))

    _section(story, "生成情報", styles)
    story.append(
        _key_value_table(
            [
                ("プロバイダー", result.get_provider_display()),
                ("モデル", result.model_name or "未設定"),
                ("ステータス", result.get_status_display()),
                ("生成日時", result.created_at),
            ],
            styles,
        )
    )

    _section(story, "入力条件", styles)
    story.append(
        _key_value_table(
            [
                ("地域", plan_request.region),
                ("旅行日数", plan_request.get_days_display()),
                ("移動手段", plan_request.get_transportation_display()),
                ("旅行者タイプ", plan_request.get_traveler_type_display()),
                (
                    "予算",
                    f"{_amount_or_unspecified(plan_request.budget_min)}円 - "
                    f"{_amount_or_unspecified(plan_request.budget_max)}円",
                ),
                ("補足条件", plan_request.free_text or "なし"),
            ],
            styles,
        )
    )

    _section(story, "生成された旅行プラン", styles)
    story.append(_p(result.generated_text, styles["JapaneseBody"]))
    if result.error_message:
        story.append(Spacer(1, 2 * mm))
        story.append(_p(f"エラー: {result.error_message}", styles["JapaneseSmall"]))

    _section(story, "候補スポット一覧", styles)
    if candidate_spots:
        for index, spot in enumerate(candidate_spots, start=1):
            story.append(
                _key_value_table(
                    [
                        ("スポット", f"{index}. {spot.get('name', '')}"),
                        ("カテゴリ", spot.get("category", "")),
                        ("住所", spot.get("address") or "未登録"),
                        ("滞在目安", f"{spot.get('estimated_stay_minutes', '')}分"),
                        ("Google Maps", spot.get("google_maps_url") or "未登録"),
                    ],
                    styles,
                )
            )
            story.append(Spacer(1, 2 * mm))
    else:
        story.append(_p("候補スポットは保存されていません。", styles["JapaneseBody"]))

    _section(story, "Google MapsルートURL", styles)
    story.append(_p(directions_url or "候補スポットが2件未満のため、ルートURLはありません。", styles["JapaneseBody"]))

    _section(story, "使用したプロンプト", styles)
    story.append(_p(result.prompt, styles["JapaneseSmall"]))

    _section(story, "注意事項", styles)
    story.append(
        _p(
            "このPDFは保存済みのAI生成結果、入力条件、候補スポットから作成しています。"
            "PDF生成時にGemini / OpenAI / Claude / Google Maps APIは呼び出していません。"
            "個人情報や秘密情報が含まれていないか、共有前に確認してください。",
            styles["JapaneseSmall"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
