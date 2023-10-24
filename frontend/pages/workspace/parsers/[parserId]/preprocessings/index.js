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

import WorkspaceLayout from "../../../../../layouts/workspace";

import service from "../../../../../service";

import preProcessingStyles from "../../../../../styles/PreProcessings.module.css";

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
        let preProcessing = params.data;
        return (
          <div style={{ display: "flex", flexDirection: "row" }}>
            <Button
              variant="primary"
              onClick={() => modifyBtnClickHandler(preProcessing)}
              style={{ height: 38, marginRight: 10 }}
            >
              Modify
            </Button>
            <Button
              variant="danger"
              onClick={() => deleteBtnClickHandler(preProcessing)}
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

  const getPreProcessings = () => {
    if (!parserId) return;
    service.get(`preprocessings/?parserId=${parserId}`, (response) => {
      setRowData(response.data);
    });
  };

  const addOrientationDetectionBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/preprocessings/addOrientationDetection/");
  };

  const modifyBtnClickHandler = (preProcessings) => {
    router.push(
      "/workspace/parsers/" + parserId + "/preprocessings/" + preProcessings.id + "/"
    );
  };

  const deleteBtnClickHandler = async (preProcessings) => {
    await service.delete("preprocessings/" + preProcessings.id + "/", () => {
      getPreProcessings();
    });
  };

  useEffect(() => {
    getPreProcessings();
  }, [parserId]);

  return (
    <WorkspaceLayout>
      <div className={preProcessingStyles.wrapper}>
        <h1 className={preProcessingStyles.h1}>Pre-Processing</h1>
        <div className={preProcessingStyles.actionsDiv}>
          <DropdownButton
            title="Perform Action"
            className={preProcessingStyles.performActionDropdown}
            >
            <Dropdown.Item href="#" onClick={addOrientationDetectionBtnClickHandler}>
              Add Orientation Detection
            </Dropdown.Item>
          </DropdownButton>
        </div>
        <div
          className={preProcessingStyles.agGridDiv + " ag-theme-alpine"}
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
    </WorkspaceLayout>
  );
}
