import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'

import ParserLayout from '../../../layouts/parser'

import service from '../../../service'

import parserStyles from "../../../styles/Parser.module.css"

export default function Parsers() {

  const router = useRouter()

  const [parsers, setParsers] = useState([])

  const [addLayoutForm, setAddLayoutForm] = useState({
    show: false,
    name: ""
  })

  const [addRoutingForm, setAddRoutingForm] = useState({
    show: false,
    name: ""
  })

  const [trashConfirmForm, setTrashConfirmForm] = useState({
    show: false,
    isValid: true,
    name: "",
    errorMessage: ""
  })

  const getParsers = () => {
    service.get("parsers/", (response)=> {
      setParsers(response.data)
    })
  }

  const addLayoutBtnClickHandler = () => {
    setAddLayoutForm(
      produce((draft) => {
        draft.show = true
      })
    )
  }

  const  layoutNameChangeHandler = (e) => {
    setAddLayoutForm(
      produce((draft) => {
        draft.name = e.target.value
      })
    )
  }


  const confirmAddLayoutBtnClickHandler = () => {
    service.post("parsers/", {
      type: "LAYOUT",
      name: addLayoutForm.name,
      ocr: {
        "ocr_type": "NO_OCR",
        "google_vision_ocr_api_key": ""
      }
    }, () => {
      getParsers()
      setAddLayoutForm(
        produce((draft) => {
          draft.show = false
        })
      )
    })
  }

  const addRoutingBtnClickHandler = () => {
    setAddRoutingForm(
      produce((draft) => {
        draft.show = true
      })
    )
  }

  const routingNameChangeHandler = (e) => {
    setAddRoutingForm(
      produce((draft) => {
        draft.name = e.target.value
      })
    )
  }


  const confirmAddRoutingBtnClickHandler = () => {
    service.post("parsers/", {
      type: "ROUTING",
      name: addRoutingForm.name,
      ocr: {
        "ocr_type": "NO_OCR",
        "google_vision_ocr_api_key": ""
      }
    }, () => {
      getParsers()
      setAddLayoutForm(
        produce((draft) => {
          draft.show = false
        })
      )
    })
  }

  const trashLayoutNameChangeHandler = (e) => {
    setTrashConfirmForm(
      produce((draft) => {
        draft.name = e.target.value
      })
    )
  }

  const closeLayoutBtnClickHandler = () => {
    setAddLayoutForm(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const closeRoutingBtnClickHandler = () => {
    setAddRoutingForm(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const trashClickHandler = () => {
    console.log("ok")
    setTrashConfirmForm(
      produce((draft) => {
        draft.show = true
      })
    )
  }

  const confirmTrashHandler = (parserId) => {
    if (trashConfirmForm.name != parsers.find(p => p.id == parserId).name) {
      setTrashConfirmForm(
        produce((draft) => {
          draft.isValid = false
          draft.errorMessage = "Parser name does not match."
        })
      )
      return
    } else {
      setTrashConfirmForm(
        produce((draft) => {
          draft.isValid = true
          draft.errorMessage = ""
        })
      )
    }
    service.delete("parsers/" + parserId + "/", (response) => {
      if (response.status == 204) {
        setTrashConfirmForm(
          produce((draft) => {
            draft.show = false
          })
        )
        getParsers()
      } else {
        setTrashConfirmForm(
          produce((draft) => {
            draft.isValid = false
            draft.errorMessage = "Delete parser failed. Please consult system administrator."
          })
        )
        return
      }
    })
  }

  const closeTrashHandler = () => {
    setTrashConfirmForm(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  useEffect(() => {
    getParsers()
  }, [])

  return (
    <ParserLayout>
      <h1 className={parserStyles.h1}>Parsers</h1>
      <ul className={parserStyles.parsersUl}>
        <li className={parserStyles.addParserLi} onClick={() => addLayoutBtnClickHandler()}>
          <div className={parserStyles.parserName}>
            <span>Add New Parser</span>
          </div>
          <div className={parserStyles.parserActions}>
            <i className="bi bi-trash"></i>
          </div>
        </li>
        <Modal show={addLayoutForm.show} onHide={closeLayoutBtnClickHandler} centered>
          <Modal.Header closeButton>
            <Modal.Title>Add Parser</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group className="mb-3" controlId="layoutNameControlInput">
                <Form.Label>Name</Form.Label>
                <Form.Control type="text"
                  placeholder="e.g. Water Supply"
                  value={addLayoutForm.name}
                  onChange={layoutNameChangeHandler}/>
              </Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={closeLayoutBtnClickHandler}>
              Close
            </Button>
            <Button variant="primary" onClick={confirmAddLayoutBtnClickHandler}>
              Add
            </Button>
          </Modal.Footer>
        </Modal>
        <li className={parserStyles.addParserLi}>
          <div className={parserStyles.parserName} onClick={() => addRoutingBtnClickHandler()}>
            <span>Add New Routing</span>
          </div>
          <div className={parserStyles.parserActions}>
            <i className="bi bi-trash"></i>
          </div>
        </li>
        <Modal show={addRoutingForm.show} onHide={closeRoutingBtnClickHandler} centered>
          <Modal.Header closeButton>
            <Modal.Title>Add Routing</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group className="mb-3" controlId="routingNameControlInput">
                <Form.Label>Name</Form.Label>
                <Form.Control type="text"
                  placeholder="e.g. Water Supply"
                  value={addRoutingForm.name}
                  onChange={routingNameChangeHandler}/>
              </Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={closeRoutingBtnClickHandler}>
              Close
            </Button>
            <Button variant="primary" onClick={confirmAddRoutingBtnClickHandler}>
              Add
            </Button>
          </Modal.Footer>
        </Modal>
        {parsers && parsers.length > 0 && parsers.map(parser => (
          <li key={parser.id}>
            <div className={parserStyles.parserName} onClick={() => router.push("/workspace/parsers/" + parser.id + "/rules")}>
              <span>{parser.name}</span>
            </div>
            <div className={parserStyles.parserActions}>
              <i className="bi bi-trash" onClick={trashClickHandler}></i>
              <Modal show={trashConfirmForm.show} onHide={closeTrashHandler} centered>
                <Modal.Header closeButton>
                  <Modal.Title>Delete Layout</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                  <Form>
                    <Form.Group className="mb-3" controlId="layoutNameControlInput">
                      <Form.Label>Name</Form.Label>
                      <Form.Control type="text"
                        placeholder="e.g. Water Supply"
                        value={trashConfirmForm.name}
                        onChange={trashLayoutNameChangeHandler}/>
                    </Form.Group>
                  </Form>
                  {!trashConfirmForm.isValid && (
                    <div className="formErrorMessage">
                      {trashConfirmForm.errorMessage}
                    </div>
                  )}
                </Modal.Body>
                <Modal.Footer>
                  <Button variant="secondary" onClick={closeTrashHandler}>
                    Close
                  </Button>
                  <Button variant="danger" onClick={() => confirmTrashHandler(parser.id)}>
                    Delete
                  </Button>
                </Modal.Footer>
              </Modal>
            </div>
          </li>
        ))}
      </ul>
    </ParserLayout>
  )
}
