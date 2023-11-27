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
    value: "PADDLE_OCR"
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

const chatBotOptions = [
  {
    label: "No Chatbot",
    value: "NO_CHATBOT"
  },
  {
    label: "Open AI",
    value: "OPEN_AI"
  }
]

const Settings = () => {

  const router = useRouter()

  const [parser, setParser] = useState(null)

  const [importModal , setImportModal] = useState({
    show: false,
    selectedFile: null,
    parserName: "",
    parserNameMatched: true
  })

  const getParser = () => {
    service.get("parsers/" + parserId + "/", response => {
      setParser(response.data)
    })
  }

  useEffect(() => {
    if (!router.isReady) return
    getParser()
  }, [router.isReady])

  const exportBtnClickHandler = () => {

  }

  const importBtnClickHandler = () => {

  }

  const closeImportModalHandler = () => {

  }

  const importFileChangeHandler = () => {

  }

  const parserNameChangeHandler = () => {
    
  }

  const confirmImportParserBtnClickHandler = () => {

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
    updatedOCR.paddleOCRLanguage = e.value
    setParser({
      ...parser,
      ocr: updatedOCR
    })
  }

  const ocrSaveBtnClickHandler = () => {
    updateParser()
  }

  const chatbotTypeChangeHandler = (e) => {
    let updatedChatBot = { ...parser.chatbot }
    updatedChatBot.chatbotType = e.value
    setParser({
      ...parser,
      chatbot: updatedChatBot
    })
  }

  const chatbotOpenAIResourceNameChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiResourceName = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot
    })
  }

  const chatbotOpenAIApiKeyChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiApiKey = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot
    })
  }

  const chatbotOpenAIDefaultQuestionChangeHandler = (e) => {
    let updatedChatbot = { ...parser.chatbot }
    updatedChatbot.openAiDefaultQuestion = e.target.value
    setParser({
      ...parser,
      chatbot: updatedChatbot
    })
  }

  const openAIEnabledChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.enabled = e.target.checked
    setParser({
      ...parser,
      openAi: updatedOpenAi
    })
  }

  const openAIResourceNameChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.openAiResourceName = e.target.value
    setParser({
      ...parser,
      openAi: updatedOpenAi
    })
  }

  const openAIApiKeyChangeHandler = (e) => {
    let updatedOpenAi = { ...parser.openAi }
    updatedOpenAi.openAiApiKey = e.target.value
    setParser({
      ...parser,
      openAi: updatedOpenAi
    })
  }

  const chatBotSaveBtnClickHandler = () => {
    updateParser()
  }

  const openAISaveBtnClickHandler = () => {
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
        <h1>Settings</h1>
        <Card style={{ width: '100%', marginBottom: 10 }}>
          <Card.Body>
            <Card.Title>Export / Import</Card.Title>
            <Card.Text>
              Export and Import this parser to transfer between servers
            </Card.Text>
            <Button variant="primary" style={{ marginRight: 10 }} onClick={exportBtnClickHandler}>Export</Button>
            <Button variant="primary" onClick={importBtnClickHandler}>Import</Button>
            <Modal show={importModal.show} onHide={closeImportModalHandler}>
                <Modal.Header closeButton>
                  <Modal.Title style={{ color: "red" }}>Warning, all of your parser information (name: {parser && parser.name}) will be erased!</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                  <Form.Group className="mb-3" controlId="formImportFile">
                    <Form.Label>Import file</Form.Label>
                    <Form.Control type="file" onChange={importFileChangeHandler}/>
                  </Form.Group>
                  <Form.Group className="mb-3" controlId="formImportFile">
                    <Form.Label>For safety reason, please re-type the parser name here.</Form.Label>
                    {!importModal.parserNameMatched && (
                      <Form.Label style={{ color: "red" }}>Parser name not matched</Form.Label>
                    )}
                    <Form.Control onChange={parserNameChangeHandler}/>
                  </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                  <Button variant="primary" onClick={confirmImportParserBtnClickHandler}>
                    Import
                  </Button>
                  <Button variant="secondary" onClick={closeImportModalHandler}>
                    Close
                  </Button>
                </Modal.Footer>
              </Modal>
          </Card.Body>
        </Card>
        {/*parser && parser.ocr != null && (
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
              {parser.ocr.ocrType == "PADDLE_OCR" && (
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
              <Button variant="primary" onClick={ocrSaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
              )*/}
        {parser && parser.chatbot != null && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Chat Bot</Card.Title>
              <Form.Group className="mb-3" controlId="formChatBotType">
                <Select
                  options={chatBotOptions}
                  value={chatBotOptions.find(oo => oo.value == parser.chatbot.chatbotType)}
                  onChange={(e) => chatbotTypeChangeHandler(e)}
                  menuPlacement="auto"
                  menuPosition="fixed" />
              </Form.Group>
              {parser.chatbot.chatbotType == "OPEN_AI" && (
                <>
                  <Form.Group className="mb-3" controlId="formChatbotOpenAIResourceName">
                    <Form.Label>Open AI Resource Name</Form.Label>
                    <Form.Control onChange={chatbotOpenAIResourceNameChangeHandler} value={parser.chatbot.openAiResourceName}/>
                  </Form.Group>
                  <Form.Group className="mb-3" controlId="formChatbotOpenAIApiKey">
                    <Form.Label>Open AI API KEY</Form.Label>
                    <Form.Control onChange={chatbotOpenAIApiKeyChangeHandler} value={parser.chatbot.openAiApiKey}/>
                  </Form.Group>
                  <Form.Group className="mb-3" controlId="formChatbotOpenAIDefaultQuestion">
                    <Form.Label>Open AI Default Question</Form.Label>
                    <Form.Control onChange={chatbotOpenAIDefaultQuestionChangeHandler} value={parser.chatbot.openAiDefaultQuestion}/>
                  </Form.Group>
                </>
              )}
              <Button variant="primary" onClick={chatBotSaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
        )}
        {parser && parser.openAi != null && (
          <Card style={{ width: '100%', marginBottom: 10 }}>
            <Card.Body>
              <Card.Title>Open AI</Card.Title>
              <Form.Group className="mb-3" controlId="formOpenAIEnabled">
                <Form.Check // prettier-ignore
                  type="checkbox"
                  id={`default-formOpenAIEnabled`}
                  label={`Enabled`}
                  checked={parser.openAi.enabled}
                  onChange={openAIEnabledChangeHandler}
                />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIResourceName">
                <Form.Label>Open AI Resource Name</Form.Label>
                <Form.Control onChange={openAIResourceNameChangeHandler} value={parser.openAi.openAiResourceName}/>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formOpenAIApiKey">
                <Form.Label>Open AI API KEY</Form.Label>
                <Form.Control onChange={openAIApiKeyChangeHandler} value={parser.openAi.openAiApiKey}/>
              </Form.Group>
              <Button variant="primary" onClick={openAISaveBtnClickHandler}>Save</Button>
            </Card.Body>
          </Card>
        )}
      </div>
    </WorkspaceLayout>
  )
}

export default Settings