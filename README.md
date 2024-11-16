# Finance-buddy 💸
This is a **Python console application** used for **basic financing**.

## Information about the Project
* I personally needed it so I can know how much I should invest at the end of each month to build my personal portfolio.
* I couldn't figure it out with Excel, so what better thing to do than **code it myself**.
* **ChatGPT** has definitely been used here.

## Guide
* The **.exe** file is located in **/dist/app**
* Once downloaded and executed, the app opens a **console** waiting for commands to be entered.
* **Commands**:
  * **Input / I**:
    * Awaits a command in the following format: `{DD:\MM:YYYY} {typeOfTransaction} {amountOfTransaction}`
      ```plaintext
      15:11:2024 income 250
      ```
    * Transactions can either be **Income** or **Expense**
    * Once successfully entered, the information is added to a locally stored `.txt` file.

  * **Report / R**:
    * Awaits a command in one of the following formats:
      `{month} {year}`
      ```plaintext
      January 2024
      ```
      or
      ```plaintext
      Current
      ```
    * Returns a report about the specified month.  
      **Current** returns a report about the **current month** based on the device's date and time.

  * **Back / B**:
    * Lets you back out of any command menu.  
      ```plaintext
      b
      ```

  * **Quit / Q**:
    * Quits the application no matter where you are.  
      ```plaintext
      q
      ```

  * **All commands are case-insensitive.**

  * **Shortcuts** (for the ultimate users 💀🙏):
    * `i {DD:\MM:YYYY} {typeOfTransaction} {amountOfTransaction}`: Directly inputs without going into `Input`.  
      Example:  
      ```plaintext
      i 15:11:2024 income 250
      ```

    * `r c`: Directly gives a report of the current month.  
      Example:  
      ```plaintext
      r c
      ```
## Final thoughts
If anyone has suggestions how improve and make this tool more useful/efficient I am open to them. Feel free to pull and suggest changes.
This is only my first python app so the code is really bad lol. 😭
