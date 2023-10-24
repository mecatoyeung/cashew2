import { useState, useEffect } from 'react'

import { useRouter } from 'next/router'

import Col from 'react-bootstrap/Col'
import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'

import Select from 'react-select'

import WorkspaceLayout from '../../../../../layouts/workspace'

import service from '../../../../../service'

import styles from '../../../../../styles/Settings.module.css'

const ocrOptions = [
  {
    label: "No OCR",
    value: "NO_OCR"
  },
  {
    label: "Google Vision OCR (Cloud, Paid, very good at English/Traditional Chinese/Simplified Chinese)",
    value: "GOOGLE_VISION"
  },
  {
    label: "DocTR (On Premise, Free, very good at English and cannot recognize Traditional Chinese and Simplified Chinese)",
    value: "DOCTR"
  }
]

const Settings = () => {

  const router = useRouter()

  const [parser, setParser] = useState(null)

  const getParser = () => {
    service.get("parsers/" + parserId + "/", response => {
      setParser(response.data)
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
  }, [router.isReady])

  const ocrTypeChangeHandler = (e) => {
    let updatedOCR = { ...parser.ocr }
    updatedOCR.ocrType = e.value
    setParser({
      ...parser,
      ocr: updatedOCR
    })
  }

  const googleVisionOcrApiKeyChangeHandler = (e) => {
    let updatedOCR = { ...parser.ocr }
    updatedOCR.googleVisionOcrApiKey = e.target.value
    setParser({
      ...parser,
      ocr: updatedOCR
    })
  }

  const ocrSaveBtnClickHandler = () => {
    updateParser()
  }

  const updateParser = () => {
    service.put("parsers/" + parserId + "/",
      parser,
      response => {
      }
    )
  }

  useEffect(() => {
    if (!router.isReady) return
  }, [router.isReady])

  const { parserId } = router.query

  return (
    <WorkspaceLayout>
      <div className={styles.settingsWrapper}>
        <h1>OCR</h1>
        {parser && parser.ocr != null && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>OCR</Card.Title>
              <Form.Group className="mb-3" controlId="formOCRType">
                <Select
                  options={ocrOptions}
                  value={ocrOptions.find(oo => oo.value == parser.ocr.ocrType)}
                  onChange={(e) => ocrTypeChangeHandler(e)}
                  menuPlacement="auto"
                  menuPosition="fixed" />
              </Form.Group>
              {parser.ocr.ocrType == "GOOGLE_VISION" && (
                <>
                  <Form.Group className="mb-3" controlId="formGoogleVisionOcrApiKey">
                    <Form.Label>Google Vision OCR API KEY</Form.Label>
                    <Form.Control onChange={googleVisionOcrApiKeyChangeHandler} value={parser.ocr.googleVisionOcrApiKey}/>
                  </Form.Group>
                </>
              )}
              <Button variant="primary" onClick={ocrSaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
        )}
      </div>
    </WorkspaceLayout>
  )
}

export default Settings