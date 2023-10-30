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

import RedactionForm from './_redactionForm'

export default function PreProcessing() {

  const router = useRouter()

  const { parserId, postprocessingId } = router.query

  const [postProcessing, setPostProcessing] = useState(null)

  const getPostProcessing = () => {
    if (!postprocessingId) return
    service.get("/postprocessings/" + postprocessingId + "/", (response) => {
      setPostProcessing(response.data)
    })
  }

  useEffect(() => {
    getPostProcessing()
  }, [parserId, postprocessingId])

  useEffect(() => {
  }, [parserId])

  return (
    <>
      {postProcessing && postProcessing.postProcessingType == "REDACTION" && (
        <RedactionForm type="edit" />
      )}
    </>
  )
}
