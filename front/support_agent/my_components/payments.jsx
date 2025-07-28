import { Blockquote, Center, Box, ScrollArea} from '@mantine/core';
import { IconWallet } from '@tabler/icons-react';
import { MyTable} from './tabels/payment_table'
import { useState } from 'react';
import { useDisclosure } from '@mantine/hooks';

export function Payments(props) {

  const [selectedRow, setSelectedRow] = useState(null);
  const [opened, { open, close }] = useDisclosure(false);
  const icon = <IconWallet />;
  return (
    // 1. The outer wrapper sets the maximum height.
      // This creates the boundary for our component.
      <Box className='limited-height-flex custom-font-body'>
  
        {/* 2. The inner container fills the wrapper and manages the layout.
            It now has a defined height to distribute to its children. */}
        <Blockquote color="lime" icon={icon} mt="xl" className='fill-flex-column' >
          {/* 3. The scrollable area grows to fill the remaining space.
              Since its parent (Blockquote) has a defined height, scrolling now works. */}
          <ScrollArea style={{ flexGrow: 1 }}>
          <Center  bg="var(--mantine-color-gray-light)">
            <MyTable elements={props.payments} selection={selectedRow} setSelection={setSelectedRow} opened={opened} open={open} close={close} />
  
          </Center>
  
          </ScrollArea>
          </Blockquote>
      </Box>
    );
  }