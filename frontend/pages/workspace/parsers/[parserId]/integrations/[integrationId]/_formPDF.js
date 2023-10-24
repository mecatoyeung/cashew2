import { useState, useEffect, useRef, useMemo, useCallback } from "react"
import { useRouter } from "next/router"
import Image from "next/image"

import { produce } from "immer"

import { Form } from "react-bootstrap"
import { Modal } from "react-bootstrap"
import { Button } from "react-bootstrap"
import { Dropdown } from "react-bootstrap"
import { Accordion } from "react-bootstrap"

import Select from "react-select"

import { AgGridReact } from "ag-grid-react"

import WorkspaceLayout from "../../../../../../layouts/workspace"

import service from "../../../../../../service"

import rulesStyles from "../../../../../../styles/Sources.module.css"

export default function Parsers(props) {

  const router = useRouter()

  const { parserId, integrationId } = router.query

  let pdfIntegrationTypeOptions = [
    {
      label: "Source",
      value: "SOURCE"
    },
    {
      label: "Pre Processing",
      value: "PRE_PROCESSING"
    },
    {
      label: "OCR",
      value: "OCR"
    },
    {
      label: "Post Processing",
      value: "POST_PROCESSING"
    },
  ]

  const [form, setForm] = useState({
    name: "",
    parser: parserId,
    integrationType: "PDF_INTEGRATION",
    pdfIntegrationType: "SOURCE",
    preProcessingId: null,
    postProcessingId: null,
    pdfPath: "",
    intervalSeconds: 15,
    activated: true,
    errorMessage: "",
  })

  const selectPdfIntegrationTypeChangeHandler = (e) => {
    setForm(produce((draft) => {
      draft.pdfIntegrationType = e.value
    }))
  }

  const addBtnClickHandler = () => {
    let errorMessage = "";
    if (form.name.trim() == "") {
      errorMessage = "Integration Name should not be empty."
    }
    if (form.pdfPath.trim() == "") {
      errorMessage = "PDF Path should not be empty."
    }
    setForm(
      produce((draft) => {
        draft.errorMessage = errorMessage;
      })
    );
    if (errorMessage) {
      return;
    }
    service.post(
      "/integrations/",
      {
        name: form.name,
        parser: parserId,
        integrationType: form.integrationType,
        pdfIntegrationType: form.pdfIntegrationType,
        preProcessingId: form.preProcessingId,
        postProcessingId: form.postProcessingId,
        pdfPath: form.pdfPath,
        intervalSeconds: form.intervalSeconds,
        activated: form.activated,
      },
      (response) => {
        router.push("/workspace/parsers/" + parserId + "/integrations/")
      }
    );
  };

  const backBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/integrations/")
  };

  const saveBtnClickHandler = () => {
    service.put(
      "/integrations/" + integrationId + "/",
      {
        name: form.name,
        parser: parserId,
        integrationType: form.integrationType,
        pdfIntegrationType: form.pdfIntegrationType,
        preProcessingId: form.preProcessingId,
        postProcessingId: form.postProcessingId,
        pdfPath: form.pdfPath,
        intervalSeconds: form.intervalSeconds,
        activated: form.activated,
      },
      (response) => {
        router.push("/workspace/parsers/" + parserId + "/integrations/")
      }
    )
  }

  useEffect(() => {
    if (props.type == "edit") {
      if (!integrationId) return
      service.get("/integrations/" + integrationId + "/", (response) => {
        console.log(response)
        setForm(
          produce((draft) => {
            draft.name = response.data.name
            draft.parser = parserId
            draft.integrationType = response.data.integrationType
            draft.pdfIntegrationType = response.data.pdfIntegrationType
            draft.preProcessingId = response.data.preProcessingId
            draft.postProcessingId = response.data.postProcessingId
            draft.pdfPath = response.data.pdfPath
            draft.intervalSeconds = response.data.intervalSeconds
            draft.activated = response.data.activated
          })
        )
      })
    }
  }, [parserId, integrationId])

  return (
    <WorkspaceLayout>
      <div className={rulesStyles.wrapper}>
        {props.type == "add" && (
          <h1 className={rulesStyles.h1}>Add PDF Integration</h1>
        )}
        {props.type == "edit" && (
          <h1 className={rulesStyles.h1}>Edit PDF Integration</h1>
        )}
        <Accordion defaultActiveKey="0" style={{ padding: 10 }}>
          <Accordion.Item eventKey="0">
            <Accordion.Header>Please fill in the form</Accordion.Header>
            <Accordion.Body>
              <Form>
                <Form.Group className="col-12" controlId="addForm.sourceName">
                  <Form.Label>Integration Name</Form.Label>
                  <Form.Control
                    type="name"
                    placeholder="Integration Name"
                    value={form.name}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.name = e.target.value;
                        })
                      );
                    }}
                  />
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.pdfIntegrationType">
                  <Form.Label>PDF Integration Type</Form.Label>
                  <Select
                    classNamePrefix="react-select"
                    options={pdfIntegrationTypeOptions}
                    value={pdfIntegrationTypeOptions.find(o => o.value == form.pdfIntegrationType)}
                    onChange={(e) => selectPdfIntegrationTypeChangeHandler(e)}
                    menuPlacement="auto"
                    menuPosition="fixed" />
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.sourcePath">
                  <Form.Label>PDF Output Path</Form.Label>
                  <Form.Control
                    type="name"
                    placeholder="PDF Output Path"
                    value={form.pdfPath}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.pdfPath = e.target.value;
                        })
                      );
                    }}
                  />
                </Form.Group>
                <Form.Group
                  className="col-12"
                  controlId="addForm.intervalSeconds"
                >
                  <Form.Label>Interval Seconds</Form.Label>
                  <Form.Control
                    type="number"
                    placeholder="Interval Seconds"
                    value={form.intervalSeconds}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.intervalSeconds = e.target.value;
                        })
                      );
                    }}
                  />
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.activated">
                  <Form.Check
                    type="checkbox"
                    placeholder="Activated"
                    label="activated"
                    checked={form.activated}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.activated = e.target.checked;
                        })
                      );
                    }}
                  />
                </Form.Group>
                {form.errorMessage && (
                  <p class="errorMessage">{form.errorMessage}</p>
                )}
                {props.type == "add" && (
                  <Button
                    onClick={addBtnClickHandler}
                    style={{ marginRight: 10 }}
                  >
                    Add PDF Integration
                  </Button>
                )}
                {props.type == "edit" && (
                  <Button
                    onClick={saveBtnClickHandler}
                    style={{ marginRight: 10 }}
                  >
                    Save
                  </Button>
                )}
                <Button variant="secondary" onClick={backBtnClickHandler}>
                  Back
                </Button>
              </Form>
            </Accordion.Body>
          </Accordion.Item>
        </Accordion>
      </div>
    </WorkspaceLayout>
  );
}
