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
  },
  {
    label: "PaddleOCR (On Premise, Free, very good at Simplified Chinese, good at English/Japanese/Korean and fair at Traditional Chinese)",
    value: "PADDLE"
  },
  {
    label: "Omnipage OCR (On Premise, Paid, very good at Traditional (Especially 香港常用字)/Simplified Chinese/English.)",
    value: "OMNIPAGE"
  }
]

const paddleOCRLangOptions = [
  {
    label: "Simplified Chinese",
    value: "ch"
  },
  {
    label: "English",
    value: "en"
  },
  {
    label: "Traditional Chinese",
    value: "ch_tra"
  },
  {
    label: "Japanese",
    value: "japan"
  },
  {
    label: "Korean",
    value: "korean"
  },
  {
    label: "French",
    value: "fr"
  },
  {
    label: "German",
    value: "german"
  },
  {
    label: "Vietnamese",
    value: "vi"
  }
]

const omnipageOCRLangOptions = [
  {
    label: "Traditional Chinese",
    value: "LANG_CHT"
  },
  {
    label: "Simplified Chinese",
    value: "LANG_CHS"
  },
  {
    label: "English",
    value: "LANG_ENG"
  }
]

const OCR = () => {

  const router = useRouter()

  const [parser, setParser] = useState(null)

  const getParser = () => {
    service.get("parsers/" + parserId + "/", response => {
      console.log(response.data)
      setParser(response.data)
    })
  }

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

  const paddleOCRLanguageChangeHandler = (e) => {
    let updatedOCR = { ...parser.ocr }
    updatedOCR.paddleOcrLanguage = e.value
    setParser({
      ...parser,
      ocr: updatedOCR
    })
  }

  const omnipageOCRLanguageChangeHandler = (e) => {
    let updatedOCR = { ...parser.ocr }
    updatedOCR.omnipageOcrLanguage = e.value
    setParser({
      ...parser,
      ocr: updatedOCR
    })
  }

  const debugChangeHandler = (e) => {
    console.log(e)
    let updatedOCR = { ...parser.ocr }
    updatedOCR.debug = e.target.checked
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
    getParser()
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
              {parser.ocr.ocrType == "PADDLE" && (
                <>
                  <Form.Group className="mb-3" controlId="formPaddleOcrApiKey">
                    <Form.Label>Paddle OCR Language</Form.Label>
                    <Select
                      options={paddleOCRLangOptions}
                      value={paddleOCRLangOptions.find(oo => oo.value == parser.ocr.paddleOcrLanguage)}
                      onChange={(e) => paddleOCRLanguageChangeHandler(e)}
                      menuPlacement="auto"
                      menuPosition="fixed" />
                  </Form.Group>
                </>
              )}
              {parser.ocr.ocrType == "OMNIPAGE" && (
                <>
                  <Form.Group className="mb-3" controlId="formOmnipageOcrApiKey">
                    <Form.Label>Omnipage OCR Language</Form.Label>
                    <Select
                      options={omnipageOCRLangOptions}
                      value={omnipageOCRLangOptions.find(oo => oo.value == parser.ocr.omnipageOcrLanguage)}
                      onChange={(e) => omnipageOCRLanguageChangeHandler(e)}
                      menuPlacement="auto"
                      menuPosition="fixed" />
                  </Form.Group>
                </>
              )}
              <Form.Group className="mb-3" controlId="formDebug">
                <Form.Label>Debug</Form.Label>
                <Form.Check // prettier-ignore
                  type="checkbox"
                  id={`default-debug`}
                  label={`Debug`}
                  onChange={(e) => debugChangeHandler(e)}
                  checked={parser.ocr.debug}
                />
              </Form.Group>
              <Button variant="primary" onClick={ocrSaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
        )}
      </div>
    </WorkspaceLayout>
  )
}

export default OCR