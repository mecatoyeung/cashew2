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

import service from '../../../../../../service'

import OrientationDetectionFormForm from './_orientationDetectionForm'
import ThresholdBinarizationForm from './_thresholdBinarizationForm'

export default function PreProcessing() {

  const router = useRouter()

  const { parserId, preprocessingId } = router.query

  const [preProcessing, setPreProcessing] = useState(null)

  const getPreProcessing = () => {
    if(!parserId) return
    if (!preprocessingId) return
    service.get("/preprocessings/" + preprocessingId + "/?parser_id=" + parserId, (response) => {
      setPreProcessing(response.data)
    })
  }

  useEffect(() => {
    getPreProcessing()
  }, [parserId, preprocessingId])

  return (
    <>
      {preProcessing && preProcessing.preProcessingType == "ORIENTATION_DETECTION_OPENCV" && (
        <OrientationDetectionFormForm type="edit" />
      )}
      {preProcessing && preProcessing.preProcessingType == "ORIENTATION_DETECTION_TESSERACT" && (
        <OrientationDetectionFormForm type="edit" />
      )}
      {preProcessing && preProcessing.preProcessingType == "ORIENTATION_DETECTION_DOCTR" && (
        <OrientationDetectionFormForm type="edit" />
      )}
      {preProcessing && preProcessing.preProcessingType == "THRESHOLD_BINARIZATION" && (
        <ThresholdBinarizationForm type="edit" />
      )}
    </>
  )
}
