from database import initialize_database, get_suppliers


# ============================================================
# SUPPLIER SCORING
# ============================================================

def calculate_supplier_score(
    rating,
    lead_time_days,
    supplier_location,
    delivery_location
):
    """
    Calculate a transparent supplier score.

    Score components:
    - Supplier rating: 50%
    - Lead time: 30%
    - Location: 20%
    """

    # --------------------------------------------------------
    # 1. Rating score
    # --------------------------------------------------------

    # Rating is between 0 and 5.
    rating_score = (rating / 5) * 100


    # --------------------------------------------------------
    # 2. Lead time score
    # --------------------------------------------------------

    # Lower lead time gets a higher score.
    #
    # We use 30 days as the maximum reference.
    # A supplier with 0 days gets 100.
    # A supplier with 30+ days gets 0.

    lead_time_score = max(
        0,
        100 - (lead_time_days / 30 * 100)
    )


    # --------------------------------------------------------
    # 3. Location score
    # --------------------------------------------------------

    if supplier_location.lower() == delivery_location.lower():

        location_score = 100

    else:

        location_score = 50


    # --------------------------------------------------------
    # 4. Final weighted score
    # --------------------------------------------------------

    final_score = (
        rating_score * 0.50
        + lead_time_score * 0.30
        + location_score * 0.20
    )


    return round(final_score, 2)


# ============================================================
# RANK SUPPLIERS
# ============================================================

def rank_suppliers(delivery_location):
    """
    Retrieve suppliers from SQLite and rank them
    based on the supplier scoring model.
    """

    suppliers = get_suppliers()

    ranked_suppliers = []


    for supplier in suppliers:

        score = calculate_supplier_score(
            rating=supplier["rating"],
            lead_time_days=supplier["lead_time_days"],
            supplier_location=supplier["location"],
            delivery_location=delivery_location
        )


        ranked_suppliers.append(
            {
                "id": supplier["id"],
                "name": supplier["name"],
                "location": supplier["location"],
                "rating": supplier["rating"],
                "lead_time_days": supplier["lead_time_days"],
                "payment_terms": supplier["payment_terms"],
                "contact_email": supplier["contact_email"],
                "score": score
            }
        )


    # Highest score first

    ranked_suppliers.sort(
        key=lambda supplier: supplier["score"],
        reverse=True
    )


    return ranked_suppliers


# ============================================================
# DISPLAY SUPPLIER COMPARISON
# ============================================================

def print_supplier_comparison(delivery_location):

    ranked_suppliers = rank_suppliers(delivery_location)


    print("\n==========================================")
    print("SUPPLIER SELECTION ANALYSIS")
    print("==========================================")

    print(f"\nDelivery Location: {delivery_location}")


    for position, supplier in enumerate(
        ranked_suppliers,
        start=1
    ):

        print(
            f"\n{position}. {supplier['name']}"
        )

        print(
            f"   Location: {supplier['location']}"
        )

        print(
            f"   Rating: {supplier['rating']}/5"
        )

        print(
            f"   Lead Time: {supplier['lead_time_days']} days"
        )

        print(
            f"   Payment Terms: {supplier['payment_terms']}"
        )

        print(
            f"   Score: {supplier['score']}/100"
        )


# ============================================================
# TEST PROGRAM
# ============================================================

if __name__ == "__main__":

    # Make sure the database exists

    initialize_database()


    # Our current procurement request is for Chennai

    delivery_location = "Chennai"


    # Calculate supplier ranking

    print_supplier_comparison(delivery_location)
