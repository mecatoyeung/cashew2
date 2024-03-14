import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Image from "next/image";

import { produce } from "immer";

import { Form } from "react-bootstrap";
import { Modal } from "react-bootstrap";
import { Button } from "react-bootstrap";
import Tab from "react-bootstrap/Tab";
import Tabs from "react-bootstrap/Tabs";

import ParserLayout from "../../../layouts/parser";

import service from "../../../service";

import parserStyles from "../../../styles/Parser.module.css";

export default function Parsers() {
  const router = useRouter();

  const [parsers, setParsers] = useState([]);

  const [addLayoutForm, setAddLayoutForm] = useState({
    show: false,
    name: "",
  });

  const [addDocumentClassificationForm, setAddDocumentClassificationForm] =
    useState({
      show: false,
      name: "",
    });

  const [trashConfirmForm, setTrashConfirmForm] = useState({
    show: false,
    isValid: true,
    name: "",
    errorMessage: "",
  });

  const [importModal, setImportModal] = useState({
    show: false,
    selectedFile: null,
    parserName: "",
    parserNameMatched: true,
  });

  const getParsers = () => {
    service.get("parsers/", (response) => {
      setParsers(response.data);
    });
  };

  const addParserBtnClickHandler = () => {
    setAddLayoutForm(
      produce((draft) => {
        draft.show = true;
      })
    );
  };

  const importParserBtnClickHandler = () => {
    setImportModal(
      produce((draft) => {
        draft.show = true;
      })
    );
  };

  const closeImportModalHandler = () => {
    setImportModal(
      produce((draft) => {
        draft.show = false;
      })
    );
  };

  const layoutNameChangeHandler = (e) => {
    setAddLayoutForm(
      produce((draft) => {
        draft.name = e.target.value;
      })
    );
  };

  const confirmAddLayoutBtnClickHandler = () => {
    service.post(
      "parsers/",
      {
        type: "LAYOUT",
        name: addLayoutForm.name,
        ocr: {
          ocrType: "NO_OCR",
          googleVisionOcrApiKey: "",
        },
        chatbot: {
          chatbotType: "NO_CHATBOT",
          openAiApiKey: "",
        },
        openAi: {
          enabled: false,
          openAiApiKey: "",
        },
      },
      () => {
        getParsers();
        setAddLayoutForm(
          produce((draft) => {
            draft.name = ""
            draft.show = false;
          })
        );
      }
    );
  };

  const confirmAddDocumentClassificationBtnClickHandler = () => {
    service.post(
      "parsers/",
      {
        type: "ROUTING",
        name: addDocumentClassificationForm.name,
        ocr: {
          ocrType: "NO_OCR",
          googleVisionOcrApiKey: "",
        },
        chatbot: {
          chatbotType: "NO_CHATBOT",
          openAiApiKey: "",
        },
        openAi: {
          enabled: false,
          openAiApiKey: "",
        },
      },
      () => {
        getParsers();
        setAddDocumentClassificationForm(
          produce((draft) => {
            draft.name = ""
            draft.show = false;
          })
        );
      }
    );
  };

  const addDocumentClassificationBtnClickHandler = () => {
    setAddDocumentClassificationForm(
      produce((draft) => {
        draft.show = true;
      })
    );
  };

  const documentClassificationNameChangeHandler = (e) => {
    setAddDocumentClassificationForm(
      produce((draft) => {
        draft.name = e.target.value;
      })
    );
  };

  const importFileChangeHandler = (e) => {
    setImportModal({
      ...importModal,
      selectedFile: e.target.files[0],
    });
  };

  const confirmImportParserBtnClickHandler = () => {
    const formData = new FormData();

    formData.append(
      "importParsers.json",
      importModal.selectedFile,
      importModal.selectedFile.name
    );

    service.post("parsers/import/", formData, (response) => {
      setImportModal({
        ...importModal,
        show: false,
      });
      getParsers();
    });
  };

  const trashLayoutNameChangeHandler = (e) => {
    setTrashConfirmForm(
      produce((draft) => {
        draft.name = e.target.value;
      })
    );
  };

  const closeLayoutBtnClickHandler = () => {
    setAddLayoutForm(
      produce((draft) => {
        draft.show = false;
      })
    );
  };

  const closeDocumentClassificationBtnClickHandler = () => {
    setAddDocumentClassificationForm(
      produce((draft) => {
        draft.show = false;
      })
    );
  };

  const trashClickHandler = (parserId) => {
    setTrashConfirmForm(
      produce((draft) => {
        draft.show = true;
        draft.parserId = parserId;
        draft.name = ""
        draft.isValid = true;
        draft.errorMessage = "";
      })
    );
  };

  const confirmTrashHandler = (parserId) => {
    if (
      trashConfirmForm.name !=
      parsers.find((p) => p.id == trashConfirmForm.parserId).name
    ) {
      setTrashConfirmForm(
        produce((draft) => {
          draft.name = ""
          draft.isValid = false;
          draft.errorMessage = "Parser name does not match.";
        })
      );
      return;
    } else {
      setTrashConfirmForm(
        produce((draft) => {
          draft.name = ""
          draft.isValid = true;
          draft.errorMessage = "";
        })
      );
    }
    service.delete("parsers/" + trashConfirmForm.parserId + "/", (response) => {
      console.log(response)
      if (response.status == 204) {
        setTrashConfirmForm(
          produce((draft) => {
            draft.show = false;
          })
        );
        getParsers();
      } else {
        setTrashConfirmForm(
          produce((draft) => {
            draft.isValid = false;
            draft.errorMessage =
              "Delete parser failed. Please consult system administrator.";
          })
        );
        return;
      }
    }, error => {
      console.log(error)
      setTrashConfirmForm(
          produce((draft) => {
            draft.isValid = false;
            draft.errorMessage =
              error.response.data
          })
        );
        return;
    });
  };

  const closeTrashHandler = () => {
    setTrashConfirmForm(
      produce((draft) => {
        draft.show = false;
      })
    );
  };

  useEffect(() => {
    getParsers();
  }, []);

  return (
    <ParserLayout>
      <h1 className={parserStyles.h1}>Parsers</h1>
      <div id="parserTabs">
        <Tabs defaultActiveKey="layouts">
          <Tab eventKey="layouts" title="Layouts">
            <ul className={parserStyles.parsersUl}>
              <li
                className={parserStyles.addParserLi}
                onClick={() => addParserBtnClickHandler()}
              >
                <div className={parserStyles.parserName}>
                  <span>Add New Layout</span>
                </div>
              </li>
              <Modal
                show={addLayoutForm.show}
                onHide={closeLayoutBtnClickHandler}
                centered
              >
                <Modal.Header closeButton>
                  <Modal.Title>Add Layout</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                  <Form>
                    <Form.Group
                      className="mb-3"
                      controlId="layoutNameControlInput"
                    >
                      <Form.Label>Name</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="e.g. Water Supply"
                        value={addLayoutForm.name}
                        onChange={layoutNameChangeHandler}
                      />
                    </Form.Group>
                  </Form>
                </Modal.Body>
                <Modal.Footer>
                  <Button
                    variant="secondary"
                    onClick={closeLayoutBtnClickHandler}
                  >
                    Close
                  </Button>
                  <Button
                    variant="primary"
                    onClick={confirmAddLayoutBtnClickHandler}
                  >
                    Add
                  </Button>
                </Modal.Footer>
              </Modal>
              <li
                className={parserStyles.addParserLi}
                onClick={() => importParserBtnClickHandler()}
              >
                <div className={parserStyles.parserName}>
                  <span>Import Parser</span>
                </div>
              </li>
              <Modal show={importModal.show} onHide={closeImportModalHandler}>
                <Modal.Header closeButton>
                  <Modal.Title style={{ color: "red" }}>
                    Import Parsers (Please note that multiple parsers may be
                    created)
                  </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                  <Form.Group className="mb-3" controlId="formImportFile">
                    <Form.Label>Import file</Form.Label>
                    <Form.Control
                      type="file"
                      onChange={importFileChangeHandler}
                    />
                  </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                  <Button
                    variant="primary"
                    onClick={confirmImportParserBtnClickHandler}
                  >
                    Import
                  </Button>
                  <Button variant="secondary" onClick={closeImportModalHandler}>
                    Close
                  </Button>
                </Modal.Footer>
              </Modal>
              {parsers &&
                parsers.length > 0 &&
                parsers
                  .filter((p) => p.type == "LAYOUT")
                  .map((parser) => (
                    <li key={parser.id}>
                      <div
                        className={parserStyles.parserName}
                        onClick={() =>
                          router.push(
                            "/workspace/parsers/" + parser.id + "/rules"
                          )
                        }
                      >
                        <span>{parser.name}</span>
                      </div>
                      <div className={parserStyles.parserActions}>
                        <i
                          className="bi bi-trash"
                          onClick={() => trashClickHandler(parser.id)}
                        ></i>
                      </div>
                    </li>
                  ))}
              <Modal
                show={trashConfirmForm.show}
                onHide={closeTrashHandler}
                centered
              >
                <Modal.Header closeButton>
                  <Modal.Title>Delete Layout</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                  <Form>
                    <Form.Group
                      className="mb-3"
                      controlId="layoutNameControlInput"
                    >
                      <Form.Label>Name</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="e.g. Water Supply"
                        value={trashConfirmForm.name}
                        onChange={trashLayoutNameChangeHandler}
                      />
                    </Form.Group>
                  </Form>
                  {!trashConfirmForm.isValid && (
                    <div className="formErrorMessage">
                      {trashConfirmForm.errorMessage}
                    </div>
                  )}
                </Modal.Body>
                <Modal.Footer>
                  <Button
                    variant="danger"
                    onClick={() => confirmTrashHandler()}
                  >
                    Delete
                  </Button>
                  <Button variant="secondary" onClick={closeTrashHandler}>
                    Close
                  </Button>
                </Modal.Footer>
              </Modal>
            </ul>
          </Tab>
          <Tab
            eventKey="documentClassification"
            title="Document Classification"
          >
            <ul className={parserStyles.parsersUl}>
              <li
                className={parserStyles.addParserLi}
                onClick={() => addDocumentClassificationBtnClickHandler()}
              >
                <div className={parserStyles.parserName}>
                  <span>Add New Document Classification</span>
                </div>
              </li>
              <Modal
                show={addDocumentClassificationForm.show}
                onHide={closeDocumentClassificationBtnClickHandler}
                centered
              >
                <Modal.Header closeButton>
                  <Modal.Title>Add Document Classification</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                  <Form>
                    <Form.Group
                      className="mb-3"
                      controlId="documentClassificationNameControlInput"
                    >
                      <Form.Label>Name</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="e.g. Water Supply"
                        value={addDocumentClassificationForm.name}
                        onChange={documentClassificationNameChangeHandler}
                      />
                    </Form.Group>
                  </Form>
                </Modal.Body>
                <Modal.Footer>
                  <Button
                    variant="secondary"
                    onClick={closeDocumentClassificationBtnClickHandler}
                  >
                    Close
                  </Button>
                  <Button
                    variant="primary"
                    onClick={confirmAddDocumentClassificationBtnClickHandler}
                  >
                    Add
                  </Button>
                </Modal.Footer>
              </Modal>
              {parsers &&
                parsers.length > 0 &&
                parsers
                  .filter((p) => p.type == "ROUTING")
                  .map((parser) => (
                    <li key={parser.id}>
                      <div
                        className={parserStyles.parserName}
                        onClick={() =>
                          router.push(
                            "/workspace/parsers/" + parser.id + "/rules"
                          )
                        }
                      >
                        <span>{parser.name}</span>
                      </div>
                      <div className={parserStyles.parserActions}>
                        <i
                          className="bi bi-trash"
                          onClick={() => trashClickHandler(parser.id)}
                        ></i>
                      </div>
                    </li>
                  ))}
            </ul>
          </Tab>
        </Tabs>
      </div>
    </ParserLayout>
  );
}
