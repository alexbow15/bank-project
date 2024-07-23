import React, { useState } from "react";
import Button from "./components/button";
import Header from "./components/header";
import axios from "axios";
import "./App.css";

function App() {
  //state variables
  const [accountNumber, setAccountNumber] = useState(""); //stores the account number input
  const [action, setAction] = useState<string | null>(null); //stores the current action (Deposit, Withdraw, or View Balance)
  const [amount, setAmount] = useState<number | null>(null); //stores the amount for Deposit or Withdraw
  const [message, setMessage] = useState<string>(""); //stores the status or error messages
  const [loading, setLoading] = useState(false); //indicates if a request is in progress

  //function to handle button clicks and set the corresponding action
  const handleButtonClick = (action: string) => {
    setAction(action);
    setAmount(null); //clear the amount field on action change
    setMessage(""); //clear the message on action change
  };

  //function to handle changes in the account number input
  const handleAccountNumberChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    console.log(`Account number changed: ${event.target.value}`);
    setAccountNumber(event.target.value);
  };

  //function to handle changes in the amount input
  const handleAmountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log(`Amount changed: ${event.target.value}`);
    setAmount(Number(event.target.value)); // Convert input value to a number
  };

  //function to check if an account exists
  const checkAccountExists = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/check_account", {
        params: { account_number: accountNumber },
      });
      return response.data.account_exists;
    } catch (error) {
      setMessage("An error occurred while checking the account.");
      return false;
    }
  };

  //function to create a new account with an optional initial balance
  const createAccount = async (initialBalance?: number) => {
    try {
      await axios.post("http://127.0.0.1:5000/create_account", {
        account_number: accountNumber,
        initial_balance: initialBalance ?? 0,
      });
      setMessage("Account created successfully.");
    } catch (error) {
      setMessage("An error occurred while creating the account.");
    }
  };

  //function to handle form submission for transactions and balance checks
  const handleSubmit = async () => {
    setLoading(true); //indicate that a request is in progress
    setMessage(""); //clear previous messages
    try {
      const accountExists = await checkAccountExists();
      if (!accountExists) {
        if (
          window.confirm(
            "Account does not exist. Would you like to create a new account?"
          )
        ) {
          const initialBalance =
            action === "Deposit" ? amount ?? undefined : undefined;
          await createAccount(initialBalance);
        } else {
          setMessage("Please create an account first.");
          setLoading(false);
          return;
        }
      } else if (action === "Deposit" || action === "Withdraw") {
        if (!amount) {
          setMessage("Please enter an amount.");
          setLoading(false);
          return;
        }
        const response = await axios.post(
          "http://127.0.0.1:5000/transactions",
          {
            account_number: accountNumber,
            transaction_type: action,
            amount: amount,
          }
        );
        setMessage(response.data.message || response.data.error);
      } else if (action === "View Balance") {
        //handle View Balance action
        const response = await axios.get(
          `http://127.0.0.1:5000/balance?account_number=${accountNumber}`
        );
        setMessage(`Balance: $${response.data.balance}`);
      }
    } catch (error: any) {
      if (error.response && error.response.data.error) {
        setMessage(error.response.data.error);
      } else {
        setMessage("An error occurred. Please try again.");
      }
    } finally {
      setLoading(false); //reset loading state
      setAction(null); //clear the action
      setAccountNumber(""); //clear the account number
      setAmount(null); //clear the amount
    }
  };

  return (
    <div className="app-container">
      <Header />
      <div className="button-container">
        {/* Buttons for Deposit, Withdraw, and View Balance actions */}
        <Button
          color="primary"
          onClick={() => handleButtonClick("Deposit")}
          label="Deposit"
        />
        <Button
          color="danger"
          onClick={() => handleButtonClick("Withdraw")}
          label="Withdraw"
        />
        <Button
          color="info"
          onClick={() => handleButtonClick("View Balance")}
          label="View Balance"
        />
      </div>
      <div className="message-container">{message && <p>{message}</p>}</div>
      {action && (
        <div className="form-container">
          <h2>{action}</h2>
          <label>
            Account Number:
            <input
              type="text"
              value={accountNumber}
              onChange={handleAccountNumberChange}
            />
          </label>
          {(action === "Deposit" || action === "Withdraw") && (
            <label style={{ marginLeft: "20px" }}>
              Amount:
              <input
                type="number"
                value={amount !== null ? amount : ""}
                onChange={handleAmountChange}
              />
            </label>
          )}
          <button onClick={handleSubmit} disabled={loading}>
            {loading ? "Processing..." : "Submit"}
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
