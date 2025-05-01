class Messages:
    class User:
        CREATED = "Account created successfully."
        NOT_CREATED = "The account could not be created. Please try again."
        NOT_FOUND = "User not found."
        UPDATED = "User information updated successfully."
        DELETED = "Account deleted successfully."
        USERNAME_IN_USE = "This username is already in use."
        EMAIL_IN_USE = "This email is already in use."
        REGISTRATION_SUCCESSFUL = "Registration completed. Please log in to continue."
        ALREADY_ACTIVE = "The account is already active."
        RECOVERED = "User account recovered successfully."

    class Auth:
        INVALID_CREDENTIALS = "Incorrect username or password."
        FORBIDDEN = "Permission denied for this action."

    class Password:
        INVALID = "The password does not meet the required criteria."

        class Validation:
            LENGTH = "Password must contain at least 8 characters."
            DIGIT = "Password must include at least one digit."
            UPPERCASE = "Password must include at least one uppercase letter."
            LOWERCASE = "Password must include at least one lowercase letter."
            SPECIAL_CHARACTER = "Password must include at least one special character."

    class General:
        INTERNAL_ERROR = "An unexpected error occurred. Please try again later."

    class Account:
        CREATED = "Account created successfully."
        UPDATED = "Account updated successfully."
        DELETED = "Account deleted successfully."
        NOT_FOUND = "Account not found."

    class Security:
        CREATED = "Security added successfully."
        UPDATED = "Security updated successfully."
        DELETED = "Security removed successfully."
        FETCHING = "Retrieving securities data..."
        NOT_FOUND = "Security not found."

    class External:
        COULD_NOT_FETCH = "Unable to retrieve data from external provider."

        @staticmethod
        def could_not_fetch_symbols(symbols: str | list):
            if isinstance(symbols, str):
                return f"Unable to retrieve data for ticker '{symbols}'."
            return f"Unable to retrieve data for tickers '{"', '".join(symbols)}'."

    class Trade:
        CREATED = "Trade executed successfully."
        DELETED = "Trade removed successfully."
        NOT_FOUND = "Trade not found."

    class Ledger:
        CREATED = "Ledger entry created successfully."
        DELETED = "Ledger entry removed successfully."
        NOT_FOUND = "Ledger entry not found."

    class Allocation:
        CREATING = "Generating allocation plan..."
        CREATED = "Allocation plan generated successfully."

        class Validation:
            MAX_TARGET_ALLOCATION = "The total target allocation must not exceed 100%."
            AT_LEAST_ONE_GREATER_THAN_ZERO = (
                "At least one security must have a target allocation greater than 0%."
            )
            ALLOCATION_STRATEGY_REQUIRED = "The total target allocation must equal 100%, or an allocation strategy must be selected."

    class Transaction:
        PROCESSED = "Transaction processed successfully."
        REPROCESSING_ALL = "Reprocessing all transactions..."
        REPROCESSED_ALL = "All transactions reprocessed successfully."

        @staticmethod
        def processing(type: str):
            return f"Processing {type} transaction..."

        class Validation:
            WITHDRAWN_AMOUNT_CANNOT_BE_GREATER_THAN_BUYING_POWER = (
                "Withdrawn amount exceeds available buying power."
            )

            @staticmethod
            def value_cannot_be_greater_than_buying_power(type: str):
                return f"Transaction value exceeds available buying power for type '{type}'."

            @staticmethod
            def quantity_cannot_be_greater_than_position(type: str):
                return f"Transaction quantity exceeds the current position for type '{type}'."
