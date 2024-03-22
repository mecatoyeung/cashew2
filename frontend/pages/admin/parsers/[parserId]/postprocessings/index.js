import React from "react" 
import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useRouter } from "next/router";
import Image from "next/image";

import { produce } from "immer";

import { Form } from "react-bootstrap";
import { Modal } from "react-bootstrap";
import { Button } from "react-bootstrap";
import { Dropdown, DropdownButton } from "react-bootstrap";

import Select from "react-select";

import { AgGridReact } from "ag-grid-react";

import AdminLayout from "../../../../../layouts/admin";

import service from "../../../../../service";

import postProcessingStyles from "../../../../../styles/PostProcessings.module.css";

React.useLayoutEffect = React.useEffect 

export default function Parsers() {
  const router = useRouter();

  const { parserId } = router.query;

  const gridRef = useRef();
  const [rowData, setRowData] = useState([]);
  const [columnDefs, setColumnDefs] = useState([
    { field: "id", resizable: true },
    { field: "name", resizable: true, filter: true },
    {
      field: "actions",
      resizable: true,
      width: 170,
      cellRenderer: (params) => {
        let postProcessing = params.data;
        return (
          <div style={{ display: "flex", flexDirection: "row" }}>
            <Button
              variant="primary"
              onClick={() => modifyBtnClickHandler(postProcessing)}
              style={{ height: 38, marginRight: 10 }}
            >
              Modify
            </Button>
            <Button
              variant="danger"
              onClick={() => deleteBtnClickHandler(postProcessing)}
              style={{ height: 38 }}
            >
              Delete
            </Button>
          </div>
        );
      },
    },
  ]);
  const defaultColDef = useMemo(
    () => ({
      sortable: true,
    }),
    []
  );
  const cellClickedListener = useCallback((event) => {}, []);

  const getPostProcessings = () => {
    if (!parserId) return;
    service.get(`postprocessings/?parserId=${parserId}`, (response) => {
      setRowData(response.data);
    });
  };

  const addRedactionBtnClickHandler = () => {
    router.push("/admin/parsers/" + parserId + "/postprocessings/addRedaction/");
  };

  const modifyBtnClickHandler = (postProcessings) => {
    router.push(
      "/admin/parsers/" + parserId + "/postprocessings/" + postProcessings.id + "/"
    );
  };

  const deleteBtnClickHandler = async (postProcessings) => {
    await service.delete("postprocessings/" + postProcessings.id + "/", () => {
      getPostProcessings();
    });
  };

  useEffect(() => {
    getPostProcessings();
  }, [parserId]);

  return (
    <AdminLayout>
      <div className={postProcessingStyles.wrapper}>
        <h1 className={postProcessingStyles.h1}>Pre-processing</h1>
        <div className={postProcessingStyles.actionsDiv}>
          <DropdownButton
            title="Perform Action"
            className={postProcessingStyles.performActionDropdown}
            >
            <Dropdown.Item href="#" onClick={addRedactionBtnClickHandler}>
              Add Redaction
            </Dropdown.Item>
          </DropdownButton>
        </div>
        <div
          className={postProcessingStyles.agGridDiv + " ag-theme-alpine"}
          style={{ width: "100%", height: "100%", marginTop: 20 }}
        >
          <AgGridReact
            ref={gridRef}
            rowData={rowData}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            animateRows={true}
            rowSelection="multiple"
            onCellClicked={cellClickedListener}
            onModelUpdated={(params) => {
              params.columnApi.autoSizeColumns(["id"]);
            }}
          />
        </div>
      </div>
    </AdminLayout>
  );
}
