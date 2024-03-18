import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useRouter } from "next/router";
import Image from "next/image";

import { produce } from "immer";

import { Form } from "react-bootstrap";
import { Modal } from "react-bootstrap";
import { Button } from "react-bootstrap";
import { Dropdown } from "react-bootstrap";
import { Accordion } from "react-bootstrap";

import Select from "react-select";

import { AgGridReact } from "ag-grid-react";

import AdminLayout from "../../../../../layouts/admin";

import service from "../../../../../service";

import PDFIntegrationForm from "./[integrationId]/_formPDF";

import integrationStyles from "../../../../../styles/Integrations.module.css";

export default function Parsers() {
  const router = useRouter();

  const { parserId } = router.query;

  useEffect(() => {}, [parserId]);

  return <PDFIntegrationForm type="add" />;
}
