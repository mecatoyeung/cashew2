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
        "ocrType": "NO_OCR",
        "googleVisionOcrApiKey": ""
      },
      chatbot: {
        "chatbotType": "NO_CHATBOT",
        "openAiApiKey": ""
      },
      openAi: {
        "enabled": false,
        "openAiApiKey": ""
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

  const trashClickHandler = (parserId) => {
    console.log("ok")
    setTrashConfirmForm(
      produce((draft) => {
        draft.show = true
        draft.parserId = parserId
      })
    )
  }

  const confirmTrashHandler = (parserId) => {
    console.log(trashConfirmForm)
    console.log(parsers)
    console.log(parserId)
    if (trashConfirmForm.name != parsers.find(p => p.id == trashConfirmForm.parserId).name) {
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
    service.delete("parsers/" + trashConfirmForm.parserId + "/", (response) => {
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
        {parsers && parsers.length > 0 && parsers.map(parser => (
          <li key={parser.id}>
            <div className={parserStyles.parserName} onClick={() => router.push("/workspace/parsers/" + parser.id + "/rules")}>
              <span>{parser.name}</span>
            </div>
            <div className={parserStyles.parserActions}>
              <i className="bi bi-trash" onClick={() => trashClickHandler(parser.id)}></i>
            </div>
          </li>
        ))}
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
            <Button variant="danger" onClick={() => confirmTrashHandler()}>
              Delete
            </Button>
          </Modal.Footer>
        </Modal>
      </ul>
    </ParserLayout>
  )
}
