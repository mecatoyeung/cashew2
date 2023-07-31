import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'

import ParserLayout from '../../layouts/parser'

import service from '../../service'

import parserStyles from "../../styles/Parser.module.css"

export default function Parsers() {

  const router = useRouter()

  const [parsers, setParsers] = useState([])

  const [addLayoutForm, setAddLayoutForm] = useState({
    show: false,
    name: ""
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
      name: addLayoutForm.name
    }, () => {
      getParsers()
      setAddLayoutForm(
        produce((draft) => {
          draft.show = false
        })
      )
    })
  }

  const closeLayoutBtnClickHandler = () => {
    setAddLayoutForm(
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
          <div className={parserStyles.parserName}>Add New Layout</div>
          <div className={parserStyles.parserActions}>
            <i className="bi bi-trash"></i>
          </div>
        </li>
        <Modal show={addLayoutForm.show} onHide={closeLayoutBtnClickHandler} centered>
          <Modal.Header closeButton>
            <Modal.Title>Add Layout</Modal.Title>
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
          <div className={parserStyles.parserName} onClick={() => router.push("parsers/1")}>Add New Routing</div>
          <div className={parserStyles.parserActions}>
            <i className="bi bi-trash"></i>
          </div>
        </li>
        {parsers && parsers.length > 0 && parsers.map(parser => (
          <li key={parser.id}>
            <div className={parserStyles.parserName} onClick={() => router.push("workspace/parsers/" + parser.id + "/rules")}>{parser.name}</div>
            <div className={parserStyles.parserActions}>
              <i className="bi bi-trash"></i>
            </div>
          </li>
        ))}
      </ul>
    </ParserLayout>
  )
}
