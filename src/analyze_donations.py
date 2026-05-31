from utils import DATA_PROCESSED_DIR, SUMMARY_DIR, add_share_column, load_csv, save_csv


def summarize_donations(donations):
    received = donations[donations["payment_status"].str.lower() == "received"].copy()

    donor_type_summary = (
        received.groupby("donor_type", as_index=False)
        .agg(
            donation_count=("donation_id", "count"),
            total_donation_cny=("donation_amount_cny", "sum"),
            average_donation_cny=("donation_amount_cny", "mean"),
        )
        .sort_values("total_donation_cny", ascending=False)
    )
    donor_type_summary["average_donation_cny"] = donor_type_summary[
        "average_donation_cny"
    ].round(2)
    donor_type_summary = add_share_column(
        donor_type_summary, "total_donation_cny", "donation_share"
    )

    team_donation_summary = (
        received.groupby("team", as_index=False)
        .agg(
            donation_count=("donation_id", "count"),
            team_donation_cny=("donation_amount_cny", "sum"),
        )
        .sort_values("team_donation_cny", ascending=False)
    )

    total_direct_donations = received["donation_amount_cny"].sum()
    average_donation = received["donation_amount_cny"].mean()

    return donor_type_summary, team_donation_summary, total_direct_donations, average_donation


def run_analysis():
    donations = load_csv(DATA_PROCESSED_DIR / "cleaned_donations.csv")
    (
        donor_type_summary,
        team_donation_summary,
        total_direct_donations,
        average_donation,
    ) = summarize_donations(donations)

    save_csv(donor_type_summary, SUMMARY_DIR / "donation_summary.csv")
    save_csv(team_donation_summary, SUMMARY_DIR / "donation_by_team.csv")

    print("Donation analysis finished.")
    print(f"Total direct donations: {total_direct_donations:,.0f} CNY")
    print(f"Average donation amount: {average_donation:,.2f} CNY")


if __name__ == "__main__":
    run_analysis()
