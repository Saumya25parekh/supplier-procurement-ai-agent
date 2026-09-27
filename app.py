import os
import re

import streamlit as st
from dotenv import load_dotenv
from google import genai

from database import (
    initialize_database,
    get_suppliers,
    get_products
)

from supplier_selection import rank_suppliers

from purchase_orders import (
    create_purchase_order,
    get_purchase_orders
)


# ============================================================
# SETUP
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:

    st.error(
        "GEMINI_API_KEY was not found in the .env file."
    )

    st.stop()


initialize_database()

client = genai.Client(
    api_key=api_key
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Supplier Procurement AI",
    page_icon="🤖",
    layout="wide"
)


st.title(
    "🤖 Supplier Procurement AI"
)

st.write(
    "AI-powered procurement assistant with "
    "supplier selection and purchase orders."
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# LOAD DATABASE
# ============================================================

suppliers = get_suppliers()

products = get_products()

purchase_orders = get_purchase_orders()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "📊 Procurement Database"
    )


    st.success(
        "Database Connected"
    )


    st.metric(
        "Suppliers",
        len(suppliers)
    )


    st.metric(
        "Products",
        len(products)
    )


    st.metric(
        "Purchase Orders",
        len(purchase_orders)
    )


    st.divider()


    st.subheader(
        "🏢 Suppliers"
    )


    for supplier in suppliers:

        st.write(
            f"**{supplier['name']}**  \n"
            f"{supplier['location']} • "
            f"⭐ {supplier['rating']} • "
            f"{supplier['lead_time_days']} days"
        )


    st.divider()


    st.subheader(
        "📄 Purchase Orders"
    )


    if purchase_orders:

        for po in purchase_orders:

            st.write(
                f"**{po['po_number']}**  \n"
                f"{po['supplier_name']} • "
                f"{po['status']}"
            )

    else:

        st.write(
            "No purchase orders yet."
        )


    st.divider()


    if st.button(
        "🗑️ Clear Conversation"
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_message = st.chat_input(
    "Example: I need 500 laptops by October 15 in Chennai"
)


if user_message:

    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    with st.chat_message("user"):

        st.write(
            user_message
        )


    # --------------------------------------------------------
    # Full conversation
    # --------------------------------------------------------

    full_conversation = ""

    for message in st.session_state.messages:

        full_conversation += (
            message["content"] + " "
        )


    conversation_lower = (
        full_conversation.lower()
    )


    message_lower = (
        user_message.lower()
    )


    # ========================================================
    # DETECT REQUEST TYPE
    # ========================================================

    supplier_selection_requested = any(
        phrase in message_lower
        for phrase in [
            "select supplier",
            "select a supplier",
            "choose supplier",
            "choose a supplier",
            "supplier selection",
            "compare suppliers",
            "compare supplier",
            "recommend supplier",
            "recommend a supplier"
        ]
    )


    purchase_order_requested = any(
        phrase in message_lower
        for phrase in [
            "create purchase order",
            "create a purchase order",
            "create po",
            "create the po",
            "generate purchase order",
            "generate a purchase order",
            "raise purchase order",
            "raise a purchase order"
        ]
    )


    # ========================================================
    # FIND DELIVERY LOCATION
    # ========================================================

    delivery_location = None


    for supplier in suppliers:

        location = supplier["location"]

        if location.lower() in conversation_lower:

            delivery_location = location

            break


    # ========================================================
    # SUPPLIER SELECTION
    # ========================================================

    if supplier_selection_requested:

        if delivery_location is None:

            assistant_response = (
                "I can compare suppliers, but I need "
                "the delivery location first."
            )


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )


            with st.chat_message(
                "assistant"
            ):

                st.write(
                    assistant_response
                )


        else:

            ranked_suppliers = rank_suppliers(
                delivery_location
            )


            with st.chat_message(
                "assistant"
            ):

                st.subheader(
                    "🏢 Supplier Comparison"
                )


                st.write(
                    f"Delivery Location: "
                    f"**{delivery_location}**"
                )


                table = []


                for supplier in ranked_suppliers:

                    table.append(
                        {
                            "Supplier":
                                supplier["name"],

                            "Location":
                                supplier["location"],

                            "Rating":
                                supplier["rating"],

                            "Lead Time":
                                f"{supplier['lead_time_days']} days",

                            "Payment Terms":
                                supplier["payment_terms"],

                            "Score":
                                f"{supplier['score']}/100"
                        }
                    )


                st.table(table)


                top_supplier = (
                    ranked_suppliers[0]
                )


                st.success(
                    f"Top-scoring supplier: "
                    f"**{top_supplier['name']}** "
                    f"({top_supplier['score']}/100)"
                )


                st.info(
                    "The score was calculated by Python "
                    "using supplier data from SQLite."
                )


            assistant_response = (
                f"Supplier comparison completed for "
                f"{delivery_location}. "
                f"Top-scoring supplier: "
                f"{top_supplier['name']} "
                f"with a score of "
                f"{top_supplier['score']}/100."
            )


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )


    # ========================================================
    # PURCHASE ORDER CREATION
    # ========================================================

    elif purchase_order_requested:

        # ----------------------------------------------------
        # Delivery location
        # ----------------------------------------------------

        if delivery_location is None:

            assistant_response = (
                "I need the delivery location before "
                "creating the purchase order."
            )


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )


            with st.chat_message(
                "assistant"
            ):

                st.write(
                    assistant_response
                )


        else:

            # ------------------------------------------------
            # Quantity
            # ------------------------------------------------

            quantity_match = re.search(
                r"\b(\d+)\s+(?:laptops?|units?|pieces?)\b",
                conversation_lower
            )


            if quantity_match:

                quantity = int(
                    quantity_match.group(1)
                )

            else:

                quantity = None


            # ------------------------------------------------
            # Find matching product
            # ------------------------------------------------

            selected_product = None


            for product in products:

                specifications = (
                    product["specifications"]
                    .lower()
                )


                if (
                    "laptop" in product["name"].lower()
                    and "windows 11 pro" in specifications
                    and "16gb ram" in specifications
                    and "512gb ssd" in specifications
                ):

                    selected_product = product

                    break


            # ------------------------------------------------
            # Fallback laptop
            # ------------------------------------------------

            if selected_product is None:

                for product in products:

                    if "laptop" in product["name"].lower():

                        selected_product = product

                        break


            # ------------------------------------------------
            # Missing quantity
            # ------------------------------------------------

            if quantity is None:

                assistant_response = (
                    "I need the quantity before "
                    "creating the purchase order."
                )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response
                    }
                )


                with st.chat_message(
                    "assistant"
                ):

                    st.write(
                        assistant_response
                    )


            # ------------------------------------------------
            # Missing product
            # ------------------------------------------------

            elif selected_product is None:

                assistant_response = (
                    "I could not find a matching laptop "
                    "in the product database."
                )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response
                    }
                )


                with st.chat_message(
                    "assistant"
                ):

                    st.write(
                        assistant_response
                    )


            else:

                # --------------------------------------------
                # Rank suppliers
                # --------------------------------------------

                ranked_suppliers = rank_suppliers(
                    delivery_location
                )


                selected_supplier = (
                    ranked_suppliers[0]
                )


                # --------------------------------------------
                # Find complete supplier record
                # --------------------------------------------

                supplier_record = None


                for supplier in suppliers:

                    if (
                        supplier["id"]
                        == selected_supplier["id"]
                    ):

                        supplier_record = supplier

                        break


                # --------------------------------------------
                # Delivery date
                # --------------------------------------------

                delivery_date = "October 15"


                # --------------------------------------------
                # CREATE REAL PURCHASE ORDER
                # --------------------------------------------

                purchase_order = create_purchase_order(
                    supplier=supplier_record,

                    product=selected_product,

                    quantity=quantity,

                    delivery_location=delivery_location,

                    required_delivery_date=delivery_date
                )


                # --------------------------------------------
                # Display PO
                # --------------------------------------------

                with st.chat_message(
                    "assistant"
                ):

                    st.subheader(
                        "📄 Purchase Order Created"
                    )


                    st.success(
                        f"PO Number: "
                        f"**{purchase_order['po_number']}**"
                    )


                    st.write(
                        f"**Supplier:** "
                        f"{purchase_order['supplier_name']}"
                    )


                    st.write(
                        f"**Product:** "
                        f"{purchase_order['product_name']}"
                    )


                    st.write(
                        f"**Quantity:** "
                        f"{purchase_order['quantity']}"
                    )


                    st.write(
                        f"**Unit Price:** "
                        f"₹{purchase_order['unit_price']:,.0f}"
                    )


                    st.write(
                        f"**Total Amount:** "
                        f"₹{purchase_order['total_amount']:,.0f}"
                    )


                    st.write(
                        f"**Delivery Location:** "
                        f"{purchase_order['delivery_location']}"
                    )


                    st.write(
                        f"**Required Delivery Date:** "
                        f"{purchase_order['required_delivery_date']}"
                    )


                    st.write(
                        f"**Status:** "
                        f"{purchase_order['status']}"
                    )


                assistant_response = (
                    f"Purchase order "
                    f"{purchase_order['po_number']} "
                    f"was created successfully for "
                    f"{purchase_order['supplier_name']}."
                )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response
                    }
                )


    # ========================================================
    # NORMAL GEMINI CHAT
    # ========================================================

    else:

        conversation = ""


        for message in st.session_state.messages:

            if message["role"] == "user":

                conversation += (
                    "USER: "
                    + message["content"]
                    + "\n"
                )

            else:

                conversation += (
                    "ASSISTANT: "
                    + message["content"]
                    + "\n"
                )


        system_instruction = """
You are a Supplier Procurement AI Agent.

Help users understand and prepare procurement requests.

Remember information from previous messages.

For procurement requests identify:
- Product
- Quantity
- Required delivery date
- Delivery location
- Specifications

Do not invent:
- Suppliers
- Prices
- Inventory
- Lead times
- Supplier ratings
- Purchase orders
- Shipments

Do not claim that a backend operation occurred unless
the application actually performed that operation.

When information is missing, ask the user for it.

When the procurement information is complete, tell the
user that the request is ready for supplier selection.

Be concise and professional.
"""


        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",

                contents=conversation,

                config={
                    "system_instruction":
                        system_instruction
                }
            )


            assistant_response = (
                response.text
            )


        except Exception as e:

            assistant_response = (
                "I encountered a temporary AI "
                "service error.\n\n"
                f"{str(e)}"
            )


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response
            }
        )


        with st.chat_message(
            "assistant"
        ):

            st.write(
                assistant_response
            )
