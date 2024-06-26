import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'

import EditorLayout from '../../../../../../layouts/editor'

import RuleProperties from '../../../../../../components/ruleEditor/ruleProperties'
import RegionSelector from '../../../../../../components/ruleEditor/regionSelector'
import StreamEditor from '../../../../../../components/ruleEditor/streamEditor'
import AcrobatFormFieldSelector from '../../../../../../components/ruleEditor/acrobatFormFieldSelector'

const RuleEditor = () => {

    const router = useRouter()

    let { parserId, type = "ruleProperties" } = router.query

    useEffect(() => {
    }, [router.isReady, parserId])

    return (
        <>
            {type == "ruleProperties" && (
                <RuleProperties />
            )}
            {type == "regionSelector" && (
                <RegionSelector />
            )}
            {type == "streamEditor" && (
                <StreamEditor />
            )}
            {type == "acrobatFormFieldSelector" && (
                <AcrobatFormFieldSelector />
            )}
        </>
    )

}

export default RuleEditor