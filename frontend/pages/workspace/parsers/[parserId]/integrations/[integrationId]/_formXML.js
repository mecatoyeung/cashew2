import { useState, useEffect, useRef, useMemo, useCallback } from "react"
import { useRouter } from "next/router"
import dynamic from "next/dynamic";
import Image from "next/image"

import { produce } from "immer"

import { Form } from "react-bootstrap"
import { Modal } from "react-bootstrap"
import { Button } from "react-bootstrap"
import { Dropdown } from "react-bootstrap"
import { Accordion } from "react-bootstrap"

import Select from "react-select"

import WorkspaceLayout from "../../../../../../layouts/workspace"

import service from "../../../../../../service"

import "@uiw/react-textarea-code-editor/dist.css";
import integrationsStyles from "../../../../../../styles/Integrations.module.css"

const CodeEditor = dynamic(
  () => import("@uiw/react-textarea-code-editor").then((mod) => mod.default),
  { ssr: false }
)
import rehypePrism from "rehype-prism-plus";
import rehypeRewrite from "rehype-rewrite";

export default function XMLForm(props) {
  const router = useRouter();

  const { parserId, integrationId } = router.query

  const [form, setForm] = useState({
    name: "",
    integrationType: "XML_INTEGRATION",
    xmlPath: "",
    template: "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
    intervalSeconds: 15,
    activated: true,
    errorMessage: "",
  });

  const addBtnClickHandler = () => {
    let errorMessage = "";
    if (form.name.trim() == "") {
      errorMessage = "Integration name should not be empty.";
    }
    if (form.xmlPath.trim() == "") {
      errorMessage = "XML path should not be empty.";
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
        parser: parserId,
        integrationType: form.integrationType,
        name: form.name,
        xmlPath: form.xmlPath,
        template: form.template,
        intervalSeconds: form.intervalSeconds,
        activated: form.activated,
      },
      (response) => {
        router.push("/workspace/parsers/" + parserId + "/integrations/");
      }
    );
  };

  const backBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/integrations/");
  };

  const saveBtnClickHandler = () => {
    service.put(
      "/integrations/" + integrationId + "/",
      {
        parser: parserId,
        integrationType: form.integrationType,
        name: form.name,
        xmlPath: form.xmlPath,
        template: form.template,
        intervalSeconds: form.intervalSeconds,
        activated: form.activated,
      },
      (response) => {
        router.push("/workspace/parsers/" + parserId + "/integrations/");
      }
    );
  }

  const templateChangeHandler = (e) => {
    setForm(
      produce((draft) => {
        draft.template = e.target.value;
      })
    )
  }

  useEffect(() => {
    if (props.type == "edit") {
      setForm(
        produce((draft) => {
          draft.id = props.integration.id
          draft.name = props.integration.name
          draft.integrationType = props.integration.integrationType
          draft.parser = props.integration.parser
          draft.xmlPath = props.integration.xmlPath
          draft.template = props.integration.template
          draft.pdfIntegrationType = props.integration.pdfIntegrationType
          draft.preProcessing = props.integration.preProcessing
          draft.postProcessing = props.integration.postProcessing
          draft.pdfPath = props.integration.pdfPath
          draft.intervalSeconds = props.integration.intervalSeconds,
          draft.activated = props.integration.activated
        })
      );
    }
  }, [parserId]);

  return (
    <WorkspaceLayout>
      <div className={integrationsStyles.wrapper}>
        {props.type == "add" && (
          <h1 className={integrationsStyles.h1}>Add XML Integration</h1>
        )}
        {props.type == "edit" && (
          <h1 className={integrationsStyles.h1}>Edit XML Integration</h1>
        )}
        <Accordion defaultActiveKey="0" style={{ padding: 10 }}>
          <Accordion.Item eventKey="0">
            <Accordion.Header>Please fill in the form</Accordion.Header>
            <Accordion.Body>
              <Form>
                <Form.Group className="col-12" controlId="addForm.integrationName">
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
                <Form.Group className="col-12" controlId="addForm.xmlPath">
                  <Form.Label>XML Path</Form.Label>
                  <Form.Control
                    type="name"
                    placeholder="XML Path"
                    value={form.xmlPath}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.xmlPath = e.target.value;
                        })
                      );
                    }}
                  />
                </Form.Group>
                {console.log(form)}
                <Form.Group className="col-12" controlId="addForm.sourceName">
                  <Form.Label>XML Editor</Form.Label>
                  <CodeEditor
                    value={form.template}
                    language="js"
                    placeholder="Please enter template"
                    onChange={(e) => templateChangeHandler(e)}
                    padding={15}
                    style={{
                      border: "1px solid #333",
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
                    Add XML Integration
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
