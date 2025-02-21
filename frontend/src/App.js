// App.js
import React, { useState } from "react";
import LoginPage from "./LoginPage";
import UploadPage from "./UploadPage";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Optionally, you can check if there's a token in localStorage already:
  // useEffect(() => {
  //   if (localStorage.getItem("authToken")) {
  //     setIsLoggedIn(true);
  //   }
  // }, []);

  return (
    <div>
      <h1>3D Model Upload Portal</h1>
      
      {!isLoggedIn ? (
        <LoginPage onSuccessLogin={() => setIsLoggedIn(true)} />
      ) : (
        <UploadPage />
      )}
    </div>
  );
}

export default App;