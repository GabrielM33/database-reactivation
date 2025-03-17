import logging
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import phonenumbers
from sqlalchemy.orm import Session

from backend.models import Conversation, ConversationState, Lead

logger = logging.getLogger(__name__)


class CSVProcessor:
    """
    Handles importing, validating, and exporting lead data from CSV files.
    """

    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, Optional[str]]:
        """Validate phone number and return a formatted version if valid."""
        try:
            # Ensure phone is a string
            phone_str = str(phone).strip()

            # Add + if it's missing and the number starts with a country code
            if not phone_str.startswith("+") and phone_str.isdigit():
                if phone_str.startswith("1"):  # US number
                    phone_str = "+" + phone_str
                else:
                    phone_str = "+1" + phone_str  # Assume US if no country code

            logger.info(f"Processing phone number: {phone_str}")

            # Simple validation for E.164 format
            if (
                phone_str.startswith("+")
                and phone_str[1:].isdigit()
                and len(phone_str) >= 11
            ):
                logger.info(f"Valid E.164 phone number: {phone_str}")
                return True, phone_str

            # Try using the phonenumbers library as a fallback
            try:
                parsed_number = phonenumbers.parse(phone_str, "US")
                if phonenumbers.is_valid_number(parsed_number):
                    formatted = phonenumbers.format_number(
                        parsed_number, phonenumbers.PhoneNumberFormat.E164
                    )
                    logger.info(f"Successfully validated phone number: {formatted}")
                    return True, formatted
                else:
                    logger.warning(f"Phone number parsed but invalid: {phone_str}")
            except Exception as e:
                logger.warning(f"Error parsing with phonenumbers: {str(e)}")

            # If we got here, the number is invalid
            return False, None

        except Exception as e:
            logger.error(f"Error validating phone number {phone}: {str(e)}")
            return False, None

    @classmethod
    def import_leads(cls, csv_path: str, db: Session) -> Dict[str, int]:
        """
        Import leads from a CSV file, validate the data, and store in the database.
        Returns a dictionary with counts of processed, added, updated, and failed records.
        """
        results = {"total": 0, "added": 0, "updated": 0, "failed": 0}

        try:
            # Read CSV file with phone_number as string
            df = pd.read_csv(csv_path, dtype={"phone_number": str})
            results["total"] = len(df)

            required_columns = ["name", "phone_number"]
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in CSV")

            # Process each row
            for _, row in df.iterrows():
                try:
                    # Validate phone number
                    is_valid, formatted_phone = cls.validate_phone_number(
                        row["phone_number"]
                    )
                    if not is_valid:
                        logger.warning(f"Invalid phone number: {row['phone_number']}")
                        results["failed"] += 1
                        continue

                    # Check if lead already exists
                    existing_lead = (
                        db.query(Lead)
                        .filter(Lead.phone_number == formatted_phone)
                        .first()
                    )

                    if existing_lead:
                        # Update existing lead
                        existing_lead.name = row["name"]
                        if "email" in row and pd.notna(row["email"]):
                            existing_lead.email = row["email"]

                        # Process additional columns as additional_info
                        additional_info = {}
                        for col in df.columns:
                            if col not in [
                                "name",
                                "phone_number",
                                "email",
                            ] and pd.notna(row[col]):
                                additional_info[col] = row[col]

                        if additional_info:
                            existing_lead.additional_info = str(additional_info)

                        results["updated"] += 1
                    else:
                        # Create new lead
                        new_lead = Lead(
                            name=row["name"],
                            phone_number=formatted_phone,
                            email=(
                                row.get("email")
                                if "email" in row and pd.notna(row["email"])
                                else None
                            ),
                        )

                        # Process additional columns as additional_info
                        additional_info = {}
                        for col in df.columns:
                            if col not in [
                                "name",
                                "phone_number",
                                "email",
                            ] and pd.notna(row[col]):
                                additional_info[col] = row[col]

                        if additional_info:
                            new_lead.additional_info = str(additional_info)

                        db.add(new_lead)

                        # Create initial conversation
                        conversation = Conversation(
                            lead=new_lead, state=ConversationState.NEW.value
                        )
                        db.add(conversation)

                        results["added"] += 1

                except Exception as e:
                    logger.error(f"Error processing row {row}: {str(e)}")
                    results["failed"] += 1

            # Commit changes
            db.commit()
            logger.info(f"Import completed successfully: {results}")

        except Exception as e:
            db.rollback()
            logger.error(f"Error importing leads: {str(e)}")
            raise

        return results

    @staticmethod
    def export_leads(db: Session, output_path: str) -> int:
        """
        Export leads from the database to a CSV file.
        Returns the number of exported records.
        """
        try:
            # Query all leads
            leads = db.query(Lead).all()

            # Convert to a list of dictionaries
            lead_data = []
            for lead in leads:
                lead_dict = {
                    "id": lead.id,
                    "name": lead.name,
                    "phone_number": lead.phone_number,
                    "email": lead.email,
                    "created_at": lead.created_at,
                    "updated_at": lead.updated_at,
                }

                # Get the most recent conversation state
                if lead.conversations:
                    latest_conversation = max(
                        lead.conversations, key=lambda c: c.updated_at
                    )
                    lead_dict["conversation_state"] = latest_conversation.state
                    lead_dict["last_contact"] = latest_conversation.last_contact
                    lead_dict["booking_completed"] = (
                        latest_conversation.booking_completed
                    )

                lead_data.append(lead_dict)

            # Convert to DataFrame and export
            df = pd.DataFrame(lead_data)
            df.to_csv(output_path, index=False)

            return len(lead_data)

        except Exception as e:
            logger.error(f"Error exporting leads: {str(e)}")
            raise
