import { useEffect } from 'react'

import { useRouter } from 'next/router'

import Col from 'react-bootstrap/Col'
import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'
import Table from 'react-bootstrap/Table'
import Form from 'react-bootstrap/Form'

import WorkspaceLayout from '../../../../layouts/workspace'

import styles from '../../../../../styles/Parser.module.css'

const ocrOptions = [
  {
    label: "Google Vision OCR",
    value: "GOOGLE_VISION"
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
    service.get("parsers/" + parserId, response => {
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

  const confirmImportParserBtnClickHandler = () => {

  }

  const googleVisionOcrApiKeyChangeHandler = () => {

  }

  const ocrActivatedChangeHandler = () => {

  }

  const ocrSaveBtnClickHandler = () => {

  }

  useEffect(() => {
    if (!router.isReady) return
  }, [router.isReady])

  const { parserId } = router.query

  return (
    <WorkspaceLayout>
      <div className={styles.documentsQueueTabWrapper}>
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
            {parser.ocr != null && parser.ocr.ocrType == "GOOGLE_VISION" && (
              <>
                <Form.Group className="mb-3" controlId="formGoogleVisionOcrApiKey">
                  <Form.Label>Google Vision OCR API KEY</Form.Label>
                  <Form.Control onChange={googleVisionOcrApiKeyChangeHandler} value={parser.ocr.googleVisionOcrApiKey}/>
                </Form.Group>
                <Form.Group className="mb-3" controlId="formOCRActivated">
                  <Form.Check
                    type="checkbox"
                    label={`Activated`}
                    checked={parser.ocr.activated == true}
                    onChange={ocrActivatedChangeHandler}
                  />
                </Form.Group>
              </>
            )}
            <Button variant="primary" onClick={ocrSaveBtnClickHandler}>Save</Button>
          </Card.Body>
        </Card>
      </div>
    </WorkspaceLayout>
  )
}

export default Settings