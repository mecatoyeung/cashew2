import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useRouter } from "next/router";
import Image from "next/image";

import { produce } from "immer";

import { Form } from "react-bootstrap";
import { Modal } from "react-bootstrap";
import { Button } from "react-bootstrap";
import { Dropdown } from "react-bootstrap";

import Select from "react-select";

import { AgGridReact } from "ag-grid-react";

import WorkspaceLayout from "../../../../../layouts/workspace";

import service from "../../../../../service";

import sourcesStyles from "../../../../../styles/Sources.module.css";

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
        let source = params.data;
        return (
          <div style={{ display: "flex", flexDirection: "row" }}>
            <Button
              variant="primary"
              onClick={() => modifyBtnClickHandler(source)}
              style={{ height: 38, marginRight: 10 }}
            >
              Modify
            </Button>
            <Button
              variant="danger"
              onClick={() => deleteBtnClickHandler(source)}
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

  const getSources = () => {
    if (!parserId) return;
    service.get(`sources/?parserId=${parserId}`, (response) => {
      setRowData(response.data);
    });
  };

  const addBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/sources/add/");
  };

  const modifyBtnClickHandler = (source) => {
    router.push(
      "/workspace/parsers/" + parserId + "/sources/" + source.id + "/"
    );
  };

  const deleteBtnClickHandler = async (source) => {
    await service.delete("sources/" + source.id + "/", () => {
      getSources();
    });
  };

  useEffect(() => {
    getSources();
  }, [parserId]);

  return (
    <WorkspaceLayout>
      <div className={sourcesStyles.wrapper}>
        <h1 className={sourcesStyles.h1}>Sources</h1>
        <div className={sourcesStyles.actionsDiv}>
          <Button
            className={sourcesStyles.actionBtn}
            onClick={addBtnClickHandler}
          >
            Add Source
          </Button>
        </div>
        <div
          className={sourcesStyles.agGridDiv + " ag-theme-alpine"}
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
