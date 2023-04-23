import { createContext, useState, useEffect } from "react";

import {
  fetchCurrentDatabaseCredentials,
  fetchCurrentOpenaiCredentials,
} from "@/apis/admin_apis";

export const AdminContext = createContext();

export const AdminProvider = ({ children }) => {
  const [tables, setTables] = useState([]);
  const [enums, setEnums] = useState([]);
  const [dbInfo, setDbInfo] = useState({});
  const [openaiInfo, setOpenaiInfo] = useState({});

  const loadOpenaiInfo = async () => {
    const data = await fetchCurrentOpenaiCredentials();
    if (data.status === "success") {
      setOpenaiInfo(data.OPENAI_API_KEY);
    }
  };

  const loadDbInfo = async () => {
    const data = await fetchCurrentDatabaseCredentials();
    if (data.status === "success") {
      setDbInfo({ urlString: data.DB_URL });
    }
  };

  useEffect(() => {
    loadOpenaiInfo();
    loadDbInfo();
  }, []);

  return (
    <AdminContext.Provider
      value={{
        tables,
        setTables,
        enums,
        setEnums,
        dbInfo,
        setDbInfo,
        openaiInfo,
        setOpenaiInfo,
      }}
    >
      {children}
    </AdminContext.Provider>
  );
};