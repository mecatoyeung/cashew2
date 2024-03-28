import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useRouter } from "next/router";
import Image from "next/image";

import { AgGridReact } from "ag-grid-react";

import { produce } from "immer";

import { Form } from "react-bootstrap";
import { Modal } from "react-bootstrap";
import { Button } from "react-bootstrap";
import { Dropdown } from "react-bootstrap";
import { Row, Col } from "react-bootstrap";

import Select from "react-select";

import SettingsLayout from "../../../layouts/settings";

import service from "../../../service";

import accountStyles from "../../../styles/Account.module.css";

export default function Groups() {
  const router = useRouter();

  const { parserId } = router.query;

  const gridRef = useRef();
  const [rowData, setRowData] = useState([]);
  const [columnDefs, setColumnDefs] = useState([
    { header: "Id", field: "id", resizable: true },
    { header: "Name", field: "name", resizable: true, filter: true },
    {
      header: "actions",
      field: "actions",
      resizable: true,
      width: 300,
      cellRenderer: (params) => {
        let group = params.data;
        return (
          <div style={{ display: "flex", flexDirection: "row" }}>
            <Button
              variant="primary"
              onClick={() => {
                editGroupBtnClickHandler(group);
              }}
              style={{ height: 38, marginRight: 10 }}
            >
              Edit
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

  const editGroupBtnClickHandler = (user) => {
    router.push("/settings/groups/" + user.id + "/");
  };

  const addGroupBtnClickHandler = () => {
    router.push("/settings/groups/add/");
  };

  const getGroups = () => {
    service.get(`groups/`, (response) => {
      console.log(response.data);
      setRowData(response.data);
    });
  };

  useEffect(() => {
    getGroups();
  }, [router.isReady, parserId]);

  return (
    <SettingsLayout>
      <h1 className={accountStyles.h1}>Groups</h1>
      <div className={accountStyles.groupsDiv}>
        <Form>
          <Row>
            <Col style={{ paddingLeft: 10, paddingRight: 10 }}>
              <Button onClick={addGroupBtnClickHandler}>Add Group</Button>
            </Col>
          </Row>
          <Row>
            <div
              className={accountStyles.agGridDiv + " ag-theme-alpine"}
              style={{ width: "100%", height: "640px", marginTop: 20 }}
            >
              <AgGridReact
                ref={gridRef}
                suppressRowTransform
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
          </Row>
        </Form>
      </div>
    </SettingsLayout>
  );
}
