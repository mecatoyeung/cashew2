import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Accordion } from 'react-bootstrap';

import Select from 'react-select'

import WorkspaceLayout from '../../../../../../layouts/workspace'

import service from '../../../../../../service'

import XMLForm from './_formXML'
import PDFForm from './_formPDF'

import integrationsStyles from "../../../../../../styles/Integrations.module.css"

export default function Parsers() {

  const router = useRouter()

  const { parserId, integrationId } = router.query

  const [integration, setIntegration] = useState({})

  const getIntegration = () => {
    if (!integrationId) return
    service.get("/integrations/" + integrationId + "/", (response) => {
      setIntegration(produce((draft) => {
        draft.id = response.data.id
        draft.name = response.data.name
        draft.integrationType = response.data.integrationType
        draft.parser = response.data.parser
        draft.xmlPath = response.data.xmlPath
        draft.template = response.data.template
        draft.pdfIntegrationType = response.data.pdfIntegrationType
        draft.preProcessing = response.data.preProcessing
        draft.postProcessing = response.data.postProcessing
        draft.pdfPath = response.data.pdfPath
        draft.intervalSeconds = response.data.intervalSeconds
        draft.nextRunTime = response.data.nextRunTime
      }))
    })
  }

  useEffect(() => {
    getIntegration()
  }, [parserId, integrationId])

  return (
    <>
      {integration && integration.integrationType == "XML_INTEGRATION" && (
        <XMLForm type="edit" integration={integration}/>
      )}
      {integration && integration.integrationType == "PDF_INTEGRATION" && (
        <PDFForm type="edit" integration={integration}/>
      )}
    </>
  )
}
